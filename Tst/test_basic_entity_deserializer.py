import json
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model


def test_restore_group_from_json():
    """
    Проверка восстановления группы из JSON с сохранением всех полей.
    """
    # Подготовка
    model_type = group_model
    source = model_type("Тестовый справочник")
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory()

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert type(restored) is model_type
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_restore_warehouse_from_json():
    """
    Проверка восстановления склада из JSON с сохранением всех полей.
    """
    # Подготовка
    model_type = warehouse_model
    source = model_type("Тестовый справочник")
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory()

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert type(restored) is model_type
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_reject_missing_entity_id():
    """
    Проверка исключения при отсутствии идентификатора модели.
    """
    # Подготовка
    data = {"name": "Сырье"}
    data["type"] = "Src.Models.group_model.group_model"
    field = "id"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_missing_entity_name():
    """
    Проверка исключения при отсутствии имени модели.
    """
    # Подготовка
    data = {"id": "group-1"}
    data["type"] = "Src.Models.group_model.group_model"
    field = "name"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_unknown_entity_field():
    """
    Проверка исключения при наличии неизвестного поля модели.
    """
    # Подготовка
    data = {"id": "group-1", "name": "Сырье", "extra": 1}
    data["type"] = "Src.Models.group_model.group_model"
    field = "extra"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_empty_entity_id():
    """
    Проверка исключения при пустом идентификаторе модели.
    """
    # Подготовка
    data = {"id": "", "name": "Сырье"}
    data["type"] = "Src.Models.group_model.group_model"
    field = "id"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_none_entity_id():
    """
    Проверка исключения при идентификаторе модели None.
    """
    # Подготовка
    data = {"id": None, "name": "Сырье"}
    data["type"] = "Src.Models.group_model.group_model"
    field = "id"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_numeric_entity_id():
    """
    Проверка исключения при числовом идентификаторе модели.
    """
    # Подготовка
    data = {"id": 1, "name": "Сырье"}
    data["type"] = "Src.Models.group_model.group_model"
    field = "id"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_empty_entity_name():
    """
    Проверка исключения при пустом имени модели.
    """
    # Подготовка
    data = {"id": "group-1", "name": ""}
    data["type"] = "Src.Models.group_model.group_model"
    field = "name"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_numeric_entity_name():
    """
    Проверка исключения при числовом имени модели.
    """
    # Подготовка
    data = {"id": "group-1", "name": 123}
    data["type"] = "Src.Models.group_model.group_model"
    field = "name"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_too_long_entity_name():
    """
    Проверка исключения при превышении допустимой длины имени.
    """
    # Подготовка
    data = {"id": "group-1", "name": "а" * 51}
    data["type"] = "Src.Models.group_model.group_model"
    field = "name"
    deserializer = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field
