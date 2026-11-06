import pytest
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.exception import arguments_exception
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.basic_entity_deserializer import basic_entity_deserializer
from Src.Logics.nomenclature_deserializer import nomenclature_deserializer
from Src.Logics.range_deserializer import range_deserializer
from Src.Logics.recipe_deserializer import recipe_deserializer
from Src.Logics.recipe_row_deserializer import recipe_row_deserializer
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


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


def test_factory_selects_group_deserializer():
    """
    Проверка подбора десериализатора группы.
    """
    # Подготовка
    model_type = group_model
    deserializer_type = basic_entity_deserializer
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(model_type)

    # Проверка
    assert isinstance(factory, abstract_deserialize_factory)
    assert isinstance(deserializer, abstract_deserializer)
    assert isinstance(deserializer, deserializer_type)
    assert deserializer.model_type is model_type


def test_factory_selects_warehouse_deserializer():
    """
    Проверка подбора десериализатора склада.
    """
    # Подготовка
    model_type = warehouse_model
    deserializer_type = basic_entity_deserializer
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(model_type)

    # Проверка
    assert isinstance(factory, abstract_deserialize_factory)
    assert isinstance(deserializer, abstract_deserializer)
    assert isinstance(deserializer, deserializer_type)
    assert deserializer.model_type is model_type


def test_factory_selects_range_deserializer():
    """
    Проверка подбора десериализатора единицы измерения.
    """
    # Подготовка
    model_type = range_model
    deserializer_type = range_deserializer
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(model_type)

    # Проверка
    assert isinstance(factory, abstract_deserialize_factory)
    assert isinstance(deserializer, abstract_deserializer)
    assert isinstance(deserializer, deserializer_type)
    assert deserializer.model_type is model_type


def test_factory_selects_nomenclature_deserializer():
    """
    Проверка подбора десериализатора номенклатуры по типу модели.
    """
    # Подготовка
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(nomenclature_model)

    # Проверка
    assert isinstance(deserializer, nomenclature_deserializer)
    assert deserializer.model_type is nomenclature_model
    assert deserializer.factory is factory


def test_factory_selects_recipe_deserializer():
    """
    Проверка подбора десериализатора рецепта по типу модели.
    """
    # Подготовка
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(recipe_model)

    # Проверка
    assert isinstance(deserializer, recipe_deserializer)
    assert deserializer.model_type is recipe_model
    assert deserializer.factory is factory


def test_factory_selects_recipe_row_deserializer():
    """
    Проверка подбора десериализатора строки рецепта по типу модели.
    """
    # Подготовка
    factory = deserialize_factory()

    # Действие
    deserializer = factory.create(recipe_row_model)

    # Проверка
    assert isinstance(deserializer, recipe_row_deserializer)
    assert deserializer.model_type is recipe_row_model
    assert deserializer.factory is factory


def test_factory_rejects_none_model_type():
    """
    Проверка исключения при передаче None вместо типа модели.
    """
    # Подготовка
    model_type = None
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_factory_rejects_string_model_type():
    """
    Проверка исключения при передаче строки вместо типа модели.
    """
    # Подготовка
    model_type = "range_model"
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_factory_rejects_numeric_model_type():
    """
    Проверка исключения при передаче числа вместо типа модели.
    """
    # Подготовка
    model_type = 42
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_factory_rejects_list_model_type():
    """
    Проверка исключения при передаче списка вместо типа модели.
    """
    # Подготовка
    model_type = []
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_factory_rejects_dictionary_type():
    """
    Проверка исключения для неподдерживаемого типа dict.
    """
    # Подготовка
    model_type = dict
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_factory_rejects_object_type():
    """
    Проверка исключения для неподдерживаемого типа object.
    """
    # Подготовка
    model_type = object
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.create(model_type)
    assert error.value.field == "model_type"


def test_mapping_cannot_be_changed_through_property():
    """
    Проверка сохранения внутреннего словаря фабрики при изменении его внешней копии.
    """
    # Подготовка
    factory = deserialize_factory()
    mapping = factory.mapping

    # Действие
    mapping.clear()
    deserializer = factory.create(group_model)

    # Проверка
    assert isinstance(deserializer, basic_entity_deserializer)
    assert set(factory.mapping) == {
        group_model, warehouse_model, range_model, nomenclature_model, recipe_model, recipe_row_model
    }
