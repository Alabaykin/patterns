from unittest.mock import patch

import pytest

from Src.Core.exception import arguments_exception, entity_conflict_exception
from Src.Logics.entity_service import entity_service
from Src.Logics.entity_controller import entity_controller
from Src.Logics.reference_index import reference_index
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model


def _nomenclature(service, storage, name, group):
    """Создать свободную номенклатуру с существующими ссылками."""
    return service.create("nomenclature", {
        "name": name, "full_name": name,
        "group": {"id": group.id}, "range": {"id": storage.ranges[0].id},
    })


def test_success_entity_service_delete_uses_index():
    """
    Проверка удаления использует готовый индекс без его перестройки.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        group = service.create("group", {"name": "Индексированная группа"})
        item = _nomenclature(service, storage, "Использующий товар", group)
        free = service.create("warehouse", {"name": "Свободный склад индекса"})
        assert service.find_referrers(group) == [item]

        # Действие и проверка
        with patch.object(reference_index, "rebuild", side_effect=AssertionError("Индекс уже построен")):
            with pytest.raises(entity_conflict_exception):
                service.delete("group", group.id)
            service.delete("warehouse", free.id)
            assert storage.find(free.id) is None
            assert service.find_referrers(group) == [item]
    finally:
        storage.load()


def test_success_entity_service_rewires_transitive_references_incrementally():
    """
    Изменение группы товара обновляет зависимости рецепта без перестройки всего индекса.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        first = service.create("group", {"name": "Группа A индекса"})
        second = service.create("group", {"name": "Группа B индекса"})
        item = _nomenclature(service, storage, "Товар индекса", first)
        recipe = service.create("recipe", {
            "name": "Карта индекса",
            "rows": [{
                "type": "Src.Models.recipe_row_model.recipe_row_model",
                "nomenclature": {"id": item.id}, "range": {"id": storage.ranges[0].id},
                "gross": 1, "net": 1,
            }],
        })
        # Действие
        with patch.object(reference_index, "rebuild", side_effect=AssertionError("Нельзя перестраивать весь индекс")):
            service.update("nomenclature", item.id, {
                "name": item.name, "full_name": item.full_name,
                "group": {"id": second.id}, "range": {"id": item.range.id},
            })
            first_referrers = service.find_referrers(first)
            second_referrers = service.find_referrers(second)
            service.delete("group", first.id)

        # Проверка
        assert first_referrers == []
        assert {entity.id for entity in second_referrers} == {item.id, recipe.id}
        assert recipe.rows[0].nomenclature is item
        assert item.group is second
        with pytest.raises(entity_conflict_exception):
            service.delete("group", second.id)
    finally:
        storage.load()


def test_success_entity_service_keeps_second_referrer_after_deletion():
    """
    Удаление одного пользователя не стирает из обратного индекса второго пользователя.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        group = service.create("group", {"name": "Общая группа индекса"})
        first = _nomenclature(service, storage, "Первый пользователь", group)
        second = _nomenclature(service, storage, "Второй пользователь", group)

        # Действие
        service.delete("nomenclature", first.id)

        # Проверка
        assert service.find_referrers(group) == [second]
        with pytest.raises(entity_conflict_exception):
            service.delete("group", group.id)

        # Действие
        service.delete("nomenclature", second.id)
        service.delete("group", group.id)

        # Проверка
        assert storage.find(group.id) is None
    finally:
        storage.load()


def test_success_entity_service_recoding_updates_outgoing_reference_owner():
    """
    Смена кода свободного товара переносит его исходящие ссылки на новый код владельца.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        group = service.create("group", {"name": "Группа перекодирования"})
        item = _nomenclature(service, storage, "Товар до перекодирования", group)
        old_id, old_name = item.id, item.name

        # Действие
        changed = service.update("nomenclature", old_id, {
            "id": "new-reference-owner", "name": "Товар после перекодирования", "full_name": item.full_name,
            "group": {"id": group.id}, "range": {"id": item.range.id},
        })

        # Проверка
        assert changed is item
        assert storage.find(old_id) is None
        assert storage.find("new-reference-owner") is item
        assert storage.name_owner("nomenclatures", old_name) is None
        assert service.find_referrers(group) == [item]

        # Действие
        service.delete("nomenclature", item.id)

        # Проверка
        assert service.find_referrers(group) == []
    finally:
        storage.load()


def test_raise_entity_service_cycle_keeps_reference_index_and_cache():
    """
    Отказ из-за цикла не меняет рёбра индекса, экземпляры и версию кэша.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        first = service.create("range", {"name": "База индекса"})
        second = service.create("range", {"name": "Производная индекса", "base_range": {"id": first.id}})
        revision = storage.revision

        # Действие и проверка
        with pytest.raises(arguments_exception):
            service.update("range", first.id, {"name": first.name, "base_range": {"id": second.id}})
        assert storage.revision == revision
        assert first.base_range is None
        assert second.base_range is first
        assert service.find_referrers(first) == [second]

        # Действие
        service.delete("range", second.id)

        # Проверка
        assert service.find_referrers(first) == []
    finally:
        storage.load()


def test_success_entity_service_rebuilds_after_storage_reload(tmp_path):
    """
    После загрузки сервис связывает индекс с восстановленными объектами, а не со старым снимком.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        group = service.create("group", {"name": "Сохранённая группа индекса"})
        item = _nomenclature(service, storage, "Сохранённый пользователь", group)
        path = tmp_path / "indexed_storage.json"
        storage.save(str(path))
        service.delete("nomenclature", item.id)
        assert service.find_referrers(group) == []

        # Действие
        storage.load(str(path))
        restored_group = service.get("group", group.id)
        referrers = service.find_referrers(restored_group)

        # Проверка
        assert restored_group is not group
        assert len(referrers) == 1
        assert referrers[0].id == item.id
        assert referrers[0] is not item
        assert referrers[0].group is restored_group
        with pytest.raises(entity_conflict_exception):
            service.delete("group", group.id)
    finally:
        storage.load()


def test_success_entity_service_and_controller_singleton():
    """
    Повторное создание возвращает те же сервис и контроллер и сохраняет индекс связей.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    first = entity_service(storage)
    controller = entity_controller(first)
    try:
        group = first.create("group", {"name": "Группа одиночки"})
        item = _nomenclature(first, storage, "Товар одиночки", group)

        # Действие
        with patch.object(reference_index, "rebuild", side_effect=AssertionError("Нельзя сбрасывать индекс")):
            second = entity_service(storage)
            repeated_controller = entity_controller(second)

            # Проверка
            assert second is first
            assert repeated_controller is controller
            assert second.find_referrers(group) == [item]
            with pytest.raises(entity_conflict_exception):
                second.delete("group", group.id)

        # Действие
        first.delete("nomenclature", item.id)
        second.delete("group", group.id)

        # Проверка
        assert storage.find(group.id) is None
    finally:
        storage.load()


def test_success_entity_service_keeps_reference_when_one_recipe_row_remains():
    """
    Удаление одной из двух строк не освобождает ингредиент, пока его использует другая строка.
    """
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    try:
        group = service.create("group", {"name": "Группа повторных строк"})
        item = _nomenclature(service, storage, "Ингредиент повторных строк", group)
        row = {
            "type": "Src.Models.recipe_row_model.recipe_row_model",
            "nomenclature": {"id": item.id}, "range": {"id": item.range.id},
            "gross": 1, "net": 1,
        }
        recipe = service.create("recipe", {"name": "Карта повторных строк", "rows": [row, row]})

        # Действие
        service.update("recipe", recipe.id, {"name": recipe.name, "rows": [row]})

        # Проверка
        assert service.find_referrers(item) == [recipe]
        with pytest.raises(entity_conflict_exception):
            service.delete("nomenclature", item.id)

        # Действие
        service.update("recipe", recipe.id, {"name": recipe.name, "rows": []})

        # Проверка
        assert service.find_referrers(item) == []
        service.delete("nomenclature", item.id)
    finally:
        storage.load()


def test_conflict_entity_service_duplicate_range():
    """
    Проверка обеспечения уникальности элементов в коллекции единиц измерения.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.ranges)

    # Добавляем дубликат с тем же именем
    duplicate = range_model("гр", 1.0)
    with pytest.raises(entity_conflict_exception):
        entity_service(sm).add(duplicate)

    # Количество не должно вырасти
    assert len(sm.ranges) == initial_count


def test_conflict_entity_service_duplicate_warehouse():
    """
    Проверка обеспечения уникальности складов.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.warehouses)

    # Добавляем склад с существующим именем
    duplicate = warehouse_model("Кухня")
    with pytest.raises(entity_conflict_exception):
        entity_service(sm).add(duplicate)

    assert len(sm.warehouses) == initial_count


def test_conflict_entity_service_duplicate_nomenclature():
    """
    Проверка обеспечения уникальности номенклатуры.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.nomenclatures)

    # Добавляем номенклатуру с существующим именем
    raw_group = sm.groups[0]
    kg_range = sm.ranges[0]
    duplicate = nomenclature_model("Мука пшеничная", "Мука пшеничная сорт 1", raw_group, kg_range)
    with pytest.raises(entity_conflict_exception):
        entity_service(sm).add(duplicate)

    assert len(sm.nomenclatures) == initial_count


def test_raise_entity_service_unsupported_model():
    """
    Проверка валидации типов при добавлении в хранилище.
    """
    sm = storage_manager()

    with pytest.raises(arguments_exception):
        entity_service(sm).add("не валидный объект")

    with pytest.raises(arguments_exception):
        entity_service(sm).add(12345)
