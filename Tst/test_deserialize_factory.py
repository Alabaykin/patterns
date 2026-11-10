import pytest
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.domain_deserializer import domain_deserializer
from Src.Models.group_model import group_model


def test_cannot_instantiate_abstract_deserialize_factory():
    """
    Проверка запрета создания экземпляра абстрактной фабрики десериализаторов.
    """
    # Подготовка
    factory_type = abstract_deserialize_factory

    # Действие и Проверка
    with pytest.raises(TypeError):
        factory_type()


def test_cannot_instantiate_abstract_deserializer():
    """
    Проверка запрета создания экземпляра абстрактного десериализатора.
    """
    # Подготовка
    deserializer_type = abstract_deserializer

    # Действие и Проверка
    with pytest.raises(TypeError):
        deserializer_type(group_model)


def test_factory_creates_domain_deserializer_by_json_type():
    """
    Проверка подбора общего обработчика по метке типа.
    """
    # Подготовка
    factory = deserialize_factory()
    type_name = group_model("Сырьё").type

    # Действие
    handler = factory.create(type_name)

    # Проверка
    assert isinstance(handler, domain_deserializer)
    assert handler.model_type is group_model


def test_factory_rejects_non_string_type():
    """
    Проверка запрета метки типа, переданной массивом JSON.
    """
    # Подготовка
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.deserialize({"type": []})
    assert error.value.field == "type"


def test_factory_keeps_plain_json_collections():
    """
    Проверка сохранения простых значений и структуры коллекций JSON.
    """
    # Подготовка
    factory = deserialize_factory()
    data = {"values": [1, False, None, {"name": "Пример"}]}

    # Действие
    restored = factory.deserialize(data)

    # Проверка
    assert restored == data
