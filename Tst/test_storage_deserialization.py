import json
import pytest
from Src.Core.exception import arguments_exception, operation_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


def _prepare_storage_file(tmp_path):
    """
    Подготовка исходных моделей хранилища и временного JSON-файла для проверки загрузки.
    """
    storage = storage_manager()
    storage.load()
    sources = storage.data
    path = tmp_path / "storage.json"
    storage.save(str(path))
    return storage, sources, path


def _assert_storage_unchanged(storage, sources):
    """
    Проверка сохранения исходных объектов и признака успешной загрузки при ошибке чтения.
    """
    assert storage.is_loaded is True
    current = storage.data
    for field, items in sources.items():
        assert len(current[field]) == len(items)
        for source, restored in zip(items, current[field]):
            assert restored is source


def test_storage_save_and_load_restores_all_models(tmp_path):
    """
    Проверка полного цикла сохранения и загрузки всех моделей, сформированных storage_manager.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    serializer = convert_factory()
    expected = serializer.serialize(sources)
    storage.add_group(group_model("Группа после сохранения"))
    model_types = {
        "ranges": range_model,
        "groups": group_model,
        "warehouses": warehouse_model,
        "nomenclatures": nomenclature_model,
        "recipes": recipe_model,
    }

    # Действие
    storage.load(str(path))

    # Проверка
    assert storage.is_loaded is True
    assert serializer.serialize(storage.data) == expected
    assert all(item.name != "Группа после сохранения" for item in storage.groups)
    for field, model_type in model_types.items():
        restored_items = storage.data[field]
        assert len(restored_items) == len(sources[field])
        for source, restored in zip(sources[field], restored_items):
            assert isinstance(restored, model_type)
            assert restored is not source
            assert restored.id == source.id
            assert restored.name == source.name
    for source, restored in zip(sources["recipes"], storage.recipes):
        assert restored.steps == source.steps
        assert all(isinstance(row, recipe_row_model) for row in restored.rows)
        assert restored.calculate_gross() == source.calculate_gross()
        assert restored.calculate_net() == source.calculate_net()
    flour = storage.get_by_type_and_id("nomenclature", sources["nomenclatures"][0].id)
    assert isinstance(flour, nomenclature_model)
    assert isinstance(flour.group, group_model)
    assert isinstance(flour.range, range_model)
    assert flour.range.coefficient == 1000.0
    assert flour.range.base_range.coefficient == 1.0


def test_storage_load_does_not_depend_on_collection_order(tmp_path):
    """
    Проверка загрузки вложенных моделей независимо от порядка коллекций и единиц в JSON.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["ranges"].reverse()
    data["recipes"].reverse()
    data = dict(reversed(list(data.items())))
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие
    storage.load(str(path))

    # Проверка
    assert convert_factory().serialize(storage.data) == data
    assert [item.id for item in storage.ranges] == [item["id"] for item in data["ranges"]]
    kilogram = storage.get_by_type_and_id("range", "кг")
    assert kilogram.coefficient == 1000.0
    assert kilogram.base_range.name == "гр"
    assert kilogram.base_range.base_range is None
    assert len(storage.recipes) == len(sources["recipes"])


def test_loaded_storage_can_be_saved_again(tmp_path):
    """
    Проверка повторного сохранения восстановленных моделей без изменения данных JSON.
    """
    # Подготовка
    storage, sources, source_path = _prepare_storage_file(tmp_path)
    expected = json.loads(source_path.read_text(encoding="utf-8"))
    target_path = tmp_path / "restored_storage.json"

    # Действие
    storage.load(str(source_path))
    storage.save(str(target_path))

    # Проверка
    assert json.loads(target_path.read_text(encoding="utf-8")) == expected
    assert convert_factory().serialize(storage.data) == convert_factory().serialize(sources)


def test_storage_load_rejects_model_without_type(tmp_path):
    """
    Проверка ошибки при отсутствии метки типа у модели в JSON.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["groups"][0]["type"]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "type"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_tagged_model_in_wrong_collection(tmp_path):
    """
    Проверка, что метка типа не позволяет загрузить модель в чужую коллекцию.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["groups"][0] = data["warehouses"][0]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "groups"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_accepts_empty_collections(tmp_path):
    """
    Проверка загрузки корректного пустого хранилища без повторной генерации исходных данных.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = {field: [] for field in sources}
    path.write_text(json.dumps(data), encoding="utf-8")

    # Действие
    storage.load(str(path))

    # Проверка
    assert storage.is_loaded is True
    assert storage.data == data


def test_storage_load_missing_file_keeps_previous_models(tmp_path):
    """
    Проверка собственного исключения и сохранения моделей при отсутствии JSON-файла.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    missing_path = tmp_path / "missing.json"

    # Действие и Проверка
    with pytest.raises(operation_exception):
        storage.load(str(missing_path))
    _assert_storage_unchanged(storage, sources)


def test_storage_load_broken_json_keeps_previous_models(tmp_path):
    """
    Проверка собственного исключения и сохранения моделей при ошибке синтаксиса JSON.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    path.write_text('{"ranges": [', encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(operation_exception):
        storage.load(str(path))
    _assert_storage_unchanged(storage, sources)


def test_storage_load_invalid_encoding_keeps_previous_models(tmp_path):
    """
    Проверка собственного исключения и сохранения моделей при неверной кодировке файла.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    path.write_bytes(b"\xff\xfe\x00")

    # Действие и Проверка
    with pytest.raises(operation_exception):
        storage.load(str(path))
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_list_root(tmp_path):
    """
    Проверка запрета массива вместо корневого словаря хранилища.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    path.write_text("[]", encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "data"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_missing_collection(tmp_path):
    """
    Проверка запрета неполной выгрузки с отсутствующей коллекцией рецептов.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    del data["recipes"]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "recipes"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_unknown_collection(tmp_path):
    """
    Проверка запрета неизвестной коллекции, которая иначе потерялась бы при загрузке.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["unknown"] = []
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "unknown"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_non_list_collection(tmp_path):
    """
    Проверка запрета словаря вместо списка объектов коллекции групп.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["groups"] = {}
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "groups"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_duplicate_names(tmp_path):
    """
    Проверка запрета повторных имен без учета регистра вместо перезаписи записей хранилища.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["groups"][1]["name"] = data["groups"][0]["name"].upper()
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "groups"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_duplicate_identifiers(tmp_path):
    """
    Проверка запрета разных записей с одинаковым идентификатором внутри коллекции.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["groups"][1]["id"] = data["groups"][0]["id"]
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "groups"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_late_model_error_keeps_previous_models(tmp_path):
    """
    Проверка сохранения всех прежних коллекций при ошибке вложенной строки в последней коллекции.
    """
    # Подготовка
    storage, sources, path = _prepare_storage_file(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["recipes"][0]["rows"][0]["net"] = 0
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(str(path))
    assert error.value.field == "net"
    _assert_storage_unchanged(storage, sources)


def test_storage_load_rejects_non_string_file_name():
    """
    Проверка собственного исключения при неверном типе имени файла.
    """
    # Подготовка
    storage = storage_manager()
    file_name = None

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        storage.load(file_name)
    assert error.value.field == "file_name"
