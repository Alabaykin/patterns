import json
from unittest.mock import patch
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.range_deserializer import range_deserializer
from Src.Models.range_model import range_model


def test_restore_gram_from_json():
    """
    Проверка восстановления базовой единицы измерения из JSON.
    """
    # Подготовка
    create = range_model.create_gramm
    source = create()
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory().create(range_model)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert isinstance(restored, range_model)
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.coefficient == source.coefficient
    assert serializer.serialize(restored) == serializer.serialize(source)
    if source.base_range is None:
        assert restored.base_range is None
    else:
        assert isinstance(restored.base_range, range_model)
        assert restored.base_range is not source.base_range
        assert restored.base_range.id == source.base_range.id
        assert restored.convert_to(restored.base_range, 2) == source.convert_to(source.base_range, 2)


def test_restore_kilogram_from_json():
    """
    Проверка восстановления килограмма с вложенной базовой единицей из JSON.
    """
    # Подготовка
    create = range_model.create_kilogramm
    source = create()
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory().create(range_model)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert isinstance(restored, range_model)
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.coefficient == source.coefficient
    assert serializer.serialize(restored) == serializer.serialize(source)
    if source.base_range is None:
        assert restored.base_range is None
    else:
        assert isinstance(restored.base_range, range_model)
        assert restored.base_range is not source.base_range
        assert restored.base_range.id == source.base_range.id
        assert restored.convert_to(restored.base_range, 2) == source.convert_to(source.base_range, 2)


def test_restore_liter_from_json():
    """
    Проверка восстановления литра с вложенной базовой единицей из JSON.
    """
    # Подготовка
    create = range_model.create_liter
    source = create()
    serializer = convert_factory()
    json_data = json.dumps(serializer.serialize(source), ensure_ascii=False)
    deserializer = deserialize_factory().create(range_model)

    # Действие
    restored = deserializer.deserialize(json.loads(json_data))

    # Проверка
    assert isinstance(restored, range_model)
    assert restored is not source
    assert restored.id == source.id
    assert restored.name == source.name
    assert restored.coefficient == source.coefficient
    assert serializer.serialize(restored) == serializer.serialize(source)
    if source.base_range is None:
        assert restored.base_range is None
    else:
        assert isinstance(restored.base_range, range_model)
        assert restored.base_range is not source.base_range
        assert restored.base_range.id == source.base_range.id
        assert restored.convert_to(restored.base_range, 2) == source.convert_to(source.base_range, 2)


def test_restore_deep_range_chain_through_injected_factory():
    """
    Проверка рекурсивного восстановления нескольких уровней через переданную фабрику.
    """
    # Подготовка
    gram = range_model.create_gramm()
    kilogram = range_model("кг", 1000, gram)
    ton = range_model("т", 1000, kilogram)
    data = convert_factory().serialize(ton)
    factory = deserialize_factory()
    deserializer = factory.create(range_model)

    # Действие
    with patch.object(factory, "create", wraps=factory.create) as create:
        restored = deserializer.deserialize(data)

    # Проверка
    assert deserializer.factory is factory
    assert create.call_count == 2
    assert restored.id == ton.id
    assert restored.base_range.id == kilogram.id
    assert restored.base_range.base_range.id == gram.id
    assert restored.base_range.base_range.base_range is None
    assert convert_factory().serialize(restored) == data


def test_reject_zero_range_coefficient():
    """
    Проверка исключения при нулевом коэффициенте единицы измерения.
    """
    # Подготовка
    coefficient = 0
    data = {"id": "range-1", "name": "кг", "coefficient": coefficient, "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_negative_range_coefficient():
    """
    Проверка исключения при отрицательном коэффициенте единицы измерения.
    """
    # Подготовка
    coefficient = -1
    data = {"id": "range-1", "name": "кг", "coefficient": coefficient, "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_boolean_range_coefficient():
    """
    Проверка исключения при логическом коэффициенте единицы измерения.
    """
    # Подготовка
    coefficient = True
    data = {"id": "range-1", "name": "кг", "coefficient": coefficient, "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_string_range_coefficient():
    """
    Проверка исключения при строковом коэффициенте единицы измерения.
    """
    # Подготовка
    coefficient = "1000"
    data = {"id": "range-1", "name": "кг", "coefficient": coefficient, "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_none_range_coefficient():
    """
    Проверка исключения при коэффициенте единицы измерения None.
    """
    # Подготовка
    coefficient = None
    data = {"id": "range-1", "name": "кг", "coefficient": coefficient, "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_list_nested_range():
    """
    Проверка исключения при списке вместо вложенной базовой единицы.
    """
    # Подготовка
    base_range = []
    data = {"id": "range-2", "name": "кг", "coefficient": 1000, "base_range": base_range}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_string_nested_range():
    """
    Проверка исключения при строке вместо вложенной базовой единицы.
    """
    # Подготовка
    base_range = "range-1"
    data = {"id": "range-2", "name": "кг", "coefficient": 1000, "base_range": base_range}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_numeric_nested_range():
    """
    Проверка исключения при числе вместо вложенной базовой единицы.
    """
    # Подготовка
    base_range = 1
    data = {"id": "range-2", "name": "кг", "coefficient": 1000, "base_range": base_range}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_incomplete_nested_range():
    """
    Проверка исключения при неполном словаре вложенной базовой единицы.
    """
    # Подготовка
    base_range = {"id": "range-1"}
    data = {"id": "range-2", "name": "кг", "coefficient": 1000, "base_range": base_range}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        deserializer.deserialize(data)


def test_reject_missing_range_coefficient():
    """
    Проверка запрета подмены отсутствующего коэффициента значением по умолчанию.
    """
    # Подготовка
    data = {"id": "range-1", "name": "кг", "base_range": None}
    deserializer = deserialize_factory().create(range_model)

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        deserializer.deserialize(data)
    assert error.value.field == "coefficient"


def test_reject_invalid_deserializer_factory():
    """
    Проверка типа фабрики, переданной десериализатору единиц измерения.
    """
    # Подготовка
    factory = object()

    # Действие и Проверка
    with pytest.raises(arguments_exception):
        range_deserializer(factory)
