import json
from types import SimpleNamespace
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.storage_manager import storage_manager
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


def test_restore_nomenclature_from_json():
    """
    Проверка восстановления всех полей номенклатуры и вложенных справочников из JSON.
    """
    # Подготовка
    source = nomenclature_model.create_flour()
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory()

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert isinstance(restored, nomenclature_model)
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.full_name == source.full_name
    assert isinstance(restored.group, group_model)
    assert restored.group is not source.group
    assert restored.group.id == source.group.id
    assert restored.group.name == source.group.name
    assert isinstance(restored.range, range_model)
    assert restored.range is not source.range
    assert restored.range.id == source.range.id
    assert restored.range.coefficient == 1000.0
    assert restored.range.base_range.id == source.range.base_range.id
    assert restored.range.base_range.coefficient == 1.0
    assert restored.range.base_range.base_range is None
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_restore_storage_nomenclatures_from_json():
    """
    Проверка соответствия восстановленной номенклатуры моделям, сформированным storage_manager.
    """
    # Подготовка
    storage = storage_manager()
    storage.convert(SimpleNamespace(is_first=True))
    sources = storage.nomenclatures
    serializer = convert_factory()
    expected = serializer.serialize(sources)
    json_data = json.dumps(expected, ensure_ascii=False)
    deserializer = deserialize_factory()

    # Действие
    restored = [deserializer.deserialize(data) for data in json.loads(json_data)]

    # Проверка
    assert len(restored) == len(sources)
    assert len(restored) > 0
    for source, model in zip(sources, restored):
        assert isinstance(model, nomenclature_model)
        assert model is not source
        assert model.id == source.id
        assert model.name == source.name
        assert model.full_name == source.full_name
        assert isinstance(model.group, group_model)
        assert isinstance(model.range, range_model)
    assert serializer.serialize(restored) == expected


def test_reject_missing_nomenclature_full_name():
    """
    Проверка исключения при отсутствии обязательного полного наименования.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    del data["full_name"]
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "full_name"


def test_reject_empty_nomenclature_full_name():
    """
    Проверка валидации пустого полного наименования конструктором модели.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["full_name"] = ""
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "full_name"


def test_reject_too_long_nomenclature_full_name():
    """
    Проверка валидации превышения допустимой длины полного наименования.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["full_name"] = "а" * 256
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "full_name"


def test_reject_unknown_nomenclature_field():
    """
    Проверка запрета неизвестных полей при восстановлении номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["extra"] = "Лишнее поле"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "extra"


def test_reject_null_nomenclature_group():
    """
    Проверка исключения при отсутствии обязательной группы номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["group"] = None
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_invalid_nested_group_name():
    """
    Проверка валидации полей вложенной группы номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["group"]["name"] = ""
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "name"


def test_reject_null_nomenclature_range():
    """
    Проверка исключения при отсутствии обязательной единицы измерения номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["range"] = None
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_invalid_nested_range_coefficient():
    """
    Проверка валидации коэффициента вложенной единицы измерения номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(nomenclature_model.create_flour())
    data["range"]["coefficient"] = 0
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"
