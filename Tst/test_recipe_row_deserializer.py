import json
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.recipe_row_deserializer import recipe_row_deserializer
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


def test_restore_recipe_row_from_json():
    """
    Проверка восстановления строки рецепта с сохранением имени, весов и вложенных моделей.
    """
    # Подготовка
    source = recipe_row_model.create_flour_row(0.5, 0.48)
    source.name = "Мука для основного замеса"
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert isinstance(restored, recipe_row_model)
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.gross == 0.5
    assert restored.net == 0.48
    assert restored.sub_recipe is None
    assert isinstance(restored.nomenclature, nomenclature_model)
    assert restored.nomenclature is not source.nomenclature
    assert restored.nomenclature.id == source.nomenclature.id
    assert isinstance(restored.range, range_model)
    assert restored.range.id == source.range.id
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_restore_recipe_row_with_sub_recipe():
    """
    Проверка самостоятельного восстановления строки с вложенной технологической картой.
    """
    # Подготовка
    source = recipe_row_model.create_dough_row()
    source.sub_recipe = recipe_model.create_dough_recipe()
    serializer = convert_factory()
    data = json.loads(json.dumps(serializer.serialize(source), ensure_ascii=False))
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие
    restored = deserializer.deserialize(data)

    # Проверка
    assert isinstance(restored.sub_recipe, recipe_model)
    assert restored.sub_recipe.id == source.sub_recipe.id
    assert restored.sub_recipe.calculate_gross() == source.sub_recipe.calculate_gross()
    assert restored.sub_recipe.calculate_net() == source.sub_recipe.calculate_net()
    assert serializer.serialize(restored) == data


def test_reject_missing_recipe_row_net():
    """
    Проверка исключения при отсутствии обязательного веса нетто строки рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    del data["net"]
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "net"


def test_reject_zero_recipe_row_gross():
    """
    Проверка валидации нулевого веса брутто при восстановлении строки рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    data["gross"] = 0
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "gross"


def test_reject_string_recipe_row_net():
    """
    Проверка валидации строкового значения веса нетто при восстановлении строки рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    data["net"] = "0.25"
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "net"


def test_reject_empty_recipe_row_name():
    """
    Проверка валидации имени строки независимо от имени вложенной номенклатуры.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    data["name"] = ""
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "name"


def test_reject_null_recipe_row_nomenclature():
    """
    Проверка исключения при отсутствии обязательной номенклатуры строки рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    data["nomenclature"] = None
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_invalid_sub_recipe_data():
    """
    Проверка исключения при неверной структуре вложенного рецепта строки.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_row_model.create_flour_row())
    data["sub_recipe"] = "Рецепт полуфабриката"
    deserializer = deserialize_factory().create(recipe_row_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_invalid_recipe_row_factory():
    """
    Проверка типа фабрики, переданной десериализатору строки рецепта.
    """
    # Подготовка
    factory = object()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        recipe_row_deserializer(factory)
