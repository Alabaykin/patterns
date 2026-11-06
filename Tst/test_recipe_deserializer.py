import json
from types import SimpleNamespace
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.recipe_deserializer import recipe_deserializer
from Src.Logics.storage_manager import storage_manager
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


def test_restore_storage_recipes_from_json():
    """
    Проверка соответствия загруженных рецептов и расчетов моделям, сформированным storage_manager.
    """
    # Подготовка
    storage = storage_manager()
    storage.convert(SimpleNamespace(is_first=True))
    sources = storage.recipes
    serializer = convert_factory()
    expected = serializer.serialize(sources)
    json_data = json.dumps(expected, ensure_ascii=False)
    deserializer = deserialize_factory().create(recipe_model)

    # Действие
    restored = [deserializer.deserialize(data) for data in json.loads(json_data)]

    # Проверка
    assert len(restored) == len(sources)
    assert len(restored) > 0
    for source, model in zip(sources, restored):
        assert isinstance(model, recipe_model)
        assert model is not source
        assert model.id == source.id
        assert model.name == source.name
        assert model.steps == source.steps
        assert isinstance(model.output_range, range_model)
        assert isinstance(model.target_nomenclature, nomenclature_model)
        assert len(model.rows) == len(source.rows)
        for source_row, row in zip(source.rows, model.rows):
            assert isinstance(row, recipe_row_model)
            assert row is not source_row
            assert row.id == source_row.id
            assert row.gross == source_row.gross
            assert row.net == source_row.net
        assert model.calculate_gross() == source.calculate_gross()
        assert model.calculate_net() == source.calculate_net()
    assert serializer.serialize(restored) == expected


def test_restore_recipe_with_multiple_nested_levels():
    """
    Проверка рекурсивного восстановления вложенных рецептов и пересчета граммов в килограммы.
    """
    # Подготовка
    kilogram = range_model.create_kilogramm()
    gram = kilogram.base_range
    dough = recipe_model("Тесто", [recipe_row_model.create_flour_row(0.5, 0.48)], output_range=kilogram)
    dough_row = recipe_row_model.create_dough_row(9.0, 8.0)
    dough_row.sub_recipe = dough
    semifinished = recipe_model("Полуфабрикат", [dough_row], output_range=kilogram)
    nested_row = recipe_row_model(nomenclature_model.create_cream(), kilogram, 7.0, 6.0, semifinished)
    sugar_row = recipe_row_model(nomenclature_model.create_sugar(), gram, 100.0, 90.0)
    source = recipe_model("Готовое блюдо", [nested_row, sugar_row], output_range=kilogram)
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory().create(recipe_model)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    restored_semifinished = restored.rows[0].sub_recipe
    restored_dough = restored_semifinished.rows[0].sub_recipe
    assert isinstance(restored_semifinished, recipe_model)
    assert restored_semifinished.id == semifinished.id
    assert isinstance(restored_dough, recipe_model)
    assert restored_dough.id == dough.id
    assert restored_dough.rows[0].gross == 0.5
    assert restored_dough.rows[0].net == 0.48
    assert restored.calculate_gross() == source.calculate_gross() == 0.6
    assert restored.calculate_net() == source.calculate_net() == 0.57
    assert serializer.serialize(restored) == serializer.serialize(source)


def test_restore_empty_recipe_with_null_references():
    """
    Проверка восстановления пустого рецепта с отсутствующими выходной единицей и номенклатурой.
    """
    # Подготовка
    source = recipe_model("Новый рецепт")
    data = json.loads(json.dumps(convert_factory().serialize(source), ensure_ascii=False))
    deserializer = deserialize_factory().create(recipe_model)

    # Действие
    restored = deserializer.deserialize(data)

    # Проверка
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.rows == []
    assert restored.steps == ""
    assert restored.output_range is None
    assert restored.target_nomenclature is None
    assert restored.calculate_gross() == 0.0
    assert restored.calculate_net() == 0.0


def test_restored_recipe_supports_independent_row_changes():
    """
    Проверка добавления и удаления строк восстановленной модели без изменения исходного рецепта.
    """
    # Подготовка
    source = recipe_model("Тесто", [recipe_row_model.create_flour_row(0.5, 0.48)])
    data = convert_factory().serialize(source)
    deserializer = deserialize_factory().create(recipe_model)
    restored = deserializer.deserialize(data)
    sugar_row = recipe_row_model.create_sugar_row(0.2, 0.19)

    # Действие
    restored.add_row(sugar_row)
    gross_with_sugar = restored.calculate_gross()
    net_with_sugar = restored.calculate_net()
    removed = restored.remove_row(sugar_row)

    # Проверка
    assert gross_with_sugar == 0.7
    assert net_with_sugar == 0.67
    assert removed is True
    assert restored.calculate_gross() == 0.5
    assert restored.calculate_net() == 0.48
    assert len(source.rows) == 1
    assert convert_factory().serialize(source) == data


def test_reject_missing_recipe_rows():
    """
    Проверка запрета подмены отсутствующего списка строк пустым рецептом.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    del data["rows"]
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "rows"


def test_reject_null_recipe_rows():
    """
    Проверка исключения при передаче null вместо списка строк рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["rows"] = None
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "rows"


def test_reject_dictionary_recipe_rows():
    """
    Проверка исключения при передаче словаря вместо списка строк рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["rows"] = {}
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "rows"


def test_reject_invalid_recipe_row_element():
    """
    Проверка исключения при неверном типе элемента в списке строк рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["rows"] = [123]
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_numeric_recipe_steps():
    """
    Проверка валидации типа инструкции при восстановлении рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["steps"] = 123
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "steps"


def test_reject_string_recipe_output_range():
    """
    Проверка исключения при строке вместо выходной единицы измерения рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["output_range"] = "кг"
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_incomplete_recipe_target_nomenclature():
    """
    Проверка исключения при неполных данных выходной номенклатуры рецепта.
    """
    # Подготовка
    data = convert_factory().serialize(recipe_model("Тесто"))
    data["target_nomenclature"] = {"id": "product-1", "name": "Тесто"}
    deserializer = deserialize_factory().create(recipe_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_invalid_recipe_factory():
    """
    Проверка типа фабрики, переданной десериализатору рецепта.
    """
    # Подготовка
    factory = object()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        recipe_deserializer(factory)
