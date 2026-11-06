import json
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.basic_entity_deserializer import basic_entity_deserializer
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
    deserializer = deserialize_factory().create(model_type)

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
    deserializer = deserialize_factory().create(model_type)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert type(restored) is model_type
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_reject_none_entity_data():
    """
    Проверка исключения при передаче None вместо словаря модели.
    """
    # Подготовка
    data = None
    field = "data"
    deserializer = deserialize_factory().create(group_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_list_entity_data():
    """
    Проверка исключения при передаче списка вместо словаря модели.
    """
    # Подготовка
    data = []
    field = "data"
    deserializer = deserialize_factory().create(group_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_string_entity_data():
    """
    Проверка исключения при передаче строки вместо словаря модели.
    """
    # Подготовка
    data = "{}"
    field = "data"
    deserializer = deserialize_factory().create(group_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_missing_entity_id():
    """
    Проверка исключения при отсутствии идентификатора модели.
    """
    # Подготовка
    data = {"name": "Сырье"}
    field = "id"
    deserializer = deserialize_factory().create(group_model)

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
    field = "name"
    deserializer = deserialize_factory().create(group_model)

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
    field = "extra"
    deserializer = deserialize_factory().create(group_model)

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
    field = "id"
    deserializer = deserialize_factory().create(group_model)

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
    field = "id"
    deserializer = deserialize_factory().create(group_model)

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
    field = "id"
    deserializer = deserialize_factory().create(group_model)

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
    field = "name"
    deserializer = deserialize_factory().create(group_model)

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
    field = "name"
    deserializer = deserialize_factory().create(group_model)

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
    field = "name"
    deserializer = deserialize_factory().create(group_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == field


def test_reject_none_basic_entity_model_type():
    """
    Проверка исключения при создании десериализатора без типа модели.
    """
    # Подготовка
    model_type = None
    deserializer_type = basic_entity_deserializer

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer_type(model_type)


def test_reject_string_basic_entity_model_type():
    """
    Проверка исключения при создании десериализатора со строкой вместо типа модели.
    """
    # Подготовка
    model_type = "group_model"
    deserializer_type = basic_entity_deserializer

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer_type(model_type)


def test_reject_primitive_basic_entity_model_type():
    """
    Проверка исключения при создании десериализатора для типа int.
    """
    # Подготовка
    model_type = int
    deserializer_type = basic_entity_deserializer

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer_type(model_type)
