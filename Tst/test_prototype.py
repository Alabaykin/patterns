import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum
from Src.Logics.prototype import prototype
from Src.Models.group_model import group_model
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model
from Src.Models.range_model import range_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


def test_contains_data_prototype():
    """Клон содержит подходящие модели, не меняя исходный список и прототип."""
    # Подготовка
    raw = group_model.create_raw()
    dishes = group_model.create_dishes()
    source = [raw, dishes]
    pr = prototype(source)
    filter = filter_dto()
    item = filter_item_dto("name", filter_type_enum.EQUALS, raw.name)
    filter.filters = [item]

    # Действие
    result = pr.clone(filter)
    assert len(result.data) == 1
    assert result.data[0] is raw
    result.data.clear()

    # Проверки
    assert result is not pr
    assert result.data == []
    assert pr.data == [raw, dishes]
    assert source == [raw, dishes]


def test_clone_prototype_applies_all_filters():
    """Все условия применяются совместно, модели остаются исходными объектами."""
    # Подготовка
    raw = group_model.create_raw()
    dishes = group_model.create_dishes()
    pr = prototype([raw, dishes])
    filter = filter_dto([
        filter_item_dto("name", filter_type_enum.EQUALS, raw.name),
        filter_item_dto("id", filter_type_enum.EQUALS, raw.id),
    ])

    # Действие
    result = pr.clone(filter)
    empty = pr.clone(filter_dto([filter_item_dto("name", filter_type_enum.EQUALS, "Неизвестная группа")]))
    unfiltered = pr.clone(filter_dto())

    # Проверки
    assert len(result.data) == 1
    assert result.data[0] is raw
    assert empty.data == []
    assert unfiltered.data == pr.data
    assert unfiltered.data is not pr.data


def test_clone_prototype_rejects_unknown_filter_type():
    """Неподдерживаемое условие отклоняется без изменения исходного прототипа."""
    # Подготовка
    raw = group_model.create_raw()
    pr = prototype([raw])
    filter = filter_dto([filter_item_dto("name", filter_type_enum.EQUALS, raw.name)])
    filter.filters[0].filter_type = "unknown"

    # Действие и проверки
    with pytest.raises(arguments_exception):
        pr.clone(filter)
    assert pr.data == [raw]


def test_contains_storage_transactions_prototype():
    """Прототип фильтрует транзакции первого старта, как в примере очного занятия."""
    # Подготовка
    settings = settings_model()
    settings.is_first = True
    manager = storage_manager()
    manager.convert(settings)
    filter = filter_dto()
    item = filter_item_dto("name", filter_type_enum.EQUALS, "Поступление яиц")
    filter.filters = [item]
    pr = prototype(manager.data["transactions"])

    # Действие
    result = pr.clone(filter)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0] is manager.transactions[0]
    assert result.data[0].value == 10
    assert result.data is not pr.data


def test_success_prototype_equals_like_and_id():
    """EQUALS требует полного совпадения, LIKE ищет буквальную подстроку с учётом регистра."""
    # Подготовка
    raw = group_model("Сырье")
    semi = group_model("Сырье для выпечки")
    pr = prototype([raw, semi])

    # Действие
    equals = pr.clone(filter_dto([filter_item_dto("name", "EQUALS", raw.name)]))
    like = pr.clone(filter_dto([filter_item_dto("name", "LIKE", raw.name)]))
    by_id = pr.clone(filter_dto([filter_item_dto("id", "EQUALS", semi.id)]))
    lowercase = pr.clone(filter_dto([filter_item_dto("name", "LIKE", "сырье")]))
    wildcard = pr.clone(filter_dto([filter_item_dto("name", "LIKE", "%")]))

    # Проверки
    assert equals.data == [raw]
    assert like.data == [raw, semi]
    assert by_id.data == [semi]
    assert lowercase.data == []
    assert wildcard.data == []


def test_success_one_prototype_for_all_domain_models():
    """Один класс фильтрует группы, единицы, номенклатуру и рецепты по их собственным полям."""
    # Подготовка
    unit = range_model.create_piece()
    group = group_model.create_raw()
    item = nomenclature_model("Мука", "Мука пшеничная", group, unit)
    recipe = recipe_model("Тесто", [recipe_row_model(item, unit, 1, 1)])

    for source in (group, unit, item, recipe):
        # Действие
        filter = filter_dto([filter_item_dto("id", "EQUALS", source.id)], recursive=False)
        result = prototype([source]).clone(filter)

        # Проверки
        assert len(result.data) == 1
        assert result.data[0] is source


def test_success_prototype_searches_nested_references():
    """Поиск доходит до базовой единицы, группы-владельца и ссылок строк рецепта."""
    # Подготовка
    root = group_model("Корневая группа")
    parent = group_model("Группа-владелец", root)
    child = group_model("Дочерняя группа", parent)
    gram = range_model.create_gramm()
    kilogram = range_model("кг", 1000, gram)
    item = nomenclature_model("Мука", "Мука пшеничная", child, kilogram)
    recipe = recipe_model("Тесто", [recipe_row_model(item, kilogram, 1, 1)])

    for source, target in ((child, root), (kilogram, gram), (item, root), (recipe, gram)):
        # Действие
        condition = filter_item_dto("id", "EQUALS", target.id)
        nested = prototype([source]).clone(filter_dto([condition]))
        direct = prototype([source]).clone(filter_dto([condition], recursive=False))

        # Проверки
        assert nested.data == [source]
        assert direct.data == []


def test_success_prototype_handles_cycle_and_shared_references():
    """Цикл не вызывает бесконечный обход, несколько путей не дублируют результат."""
    # Подготовка
    first = group_model("Первая")
    second = group_model("Вторая", first)
    first.parent = second
    pr = prototype([first])

    # Действие
    found = pr.clone(filter_dto([filter_item_dto("name", "EQUALS", second.name)]))
    missing = pr.clone(filter_dto([filter_item_dto("name", "EQUALS", "Нет такой группы")]))

    # Проверки
    assert found.data == [first]
    assert missing.data == []
    assert first.parent is second
    assert second.parent is first


def test_success_prototype_conditions_use_and():
    """Совпадение только одного условия не включает модель в результат."""
    # Подготовка
    raw = group_model.create_raw()
    dishes = group_model.create_dishes()
    filter = filter_dto([
        filter_item_dto("name", "EQUALS", raw.name),
        filter_item_dto("id", "EQUALS", dishes.id),
    ])

    # Действие
    result = prototype([raw, dishes]).clone(filter)

    # Проверки
    assert result.data == []


def test_raise_filter_dto_invalid_request():
    """Неверные поля, операции, типы данных и период отклоняются даже без исходных моделей."""
    # Подготовка
    cases = [
        [], {"unknown": 1}, {"filters": None}, {"recursive": "false"},
        {"filters": [None]}, {"filters": [{"field_name": "name"}]},
        {"filters": [{"field_name": "value", "value": "10"}]},
        {"filters": [{"field_name": "name", "value": 10}]},
        {"filters": [{"field_name": "name", "value": ""}]},
        {"filters": [{"field_name": "name", "filter_type": "eq", "value": "Мука"}]},
        {"filters": [{"field_name": "name", "value": "Мука", "extra": 1}]},
        {"date_from": "вчера"}, {"date_to": 10},
        {"date_from": "2026-11-20T00:00:00Z", "date_to": "2026-11-01T00:00:00Z"},
    ]
    for body in cases:
        # Действие и проверки
        with pytest.raises(arguments_exception):
            prototype([]).clone(filter_dto.from_dict(body))
