import pytest
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception, operation_exception


def test_create_base_range_success():
    """
    Создание базовой единицы измерения без передачи base_range.
    """
    # Действие
    gramm = range_model("грамм", 1)

    # Проверка
    assert gramm.name == "грамм"
    assert gramm.coefficient == 1.0
    assert gramm.base_range == gramm


def test_create_dependent_range_success():
    """
    Создание производной единицы измерения с указанием базовой.
    """
    # Подготовка
    gramm = range_model("грамм", 1)

    # Действие
    kg = range_model("кг", 1000, gramm)

    # Проверка
    assert kg.name == "кг"
    assert kg.coefficient == 1000.0
    assert kg.base_range == gramm


def test_conversion_to_base_success():
    """
    Пересчет значения производной единицы в базовую.
    """
    # Подготовка
    gramm = range_model("грамм", 1)
    kg = range_model("кг", 1000, gramm)

    # Действие
    result = kg.to_base(2.5)

    # Проверка (2.5 кг = 2500 грамм)
    assert result == 2500.0


def test_raise_arguments_exception_when_coefficient_is_negative():
    """
    Попытка задать отрицательный коэффициент вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        range_model("кг", -10)


def test_raise_arguments_exception_when_coefficient_is_zero():
    """
    Попытка задать нулевой коэффициент вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        range_model("кг", 0)


def test_raise_arguments_exception_when_coefficient_is_invalid_type():
    """
    Попытка задать нечисловой коэффициент вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        range_model("кг", "тысяча")


def test_raise_arguments_exception_when_base_range_is_invalid_type():
    """
    Попытка передать некорректный объект вместо base_range вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        range_model("кг", 1000, "не range_model")


def test_convert_to_between_compatible_units_success():
    """
    Успешный пересчет между совместимыми единицами измерения (тонна в килограммы).
    """
    # Подготовка: грамм - база, кг (1000 г), тонна (1_000_000 г)
    gramm = range_model("грамм", 1)
    kg = range_model("кг", 1000, gramm)
    ton = range_model("т", 1000000, gramm)

    # Действие
    result = ton.convert_to(kg, 2)

    # Проверка
    assert result == 2000.0


def test_raise_operation_exception_when_convert_incompatible_units():
    """
    Попытка пересчета между несовместимыми единицами (разные базовые единицы) вызывает operation_exception.
    """
    # Подготовка
    gramm = range_model("грамм", 1)
    kg = range_model("кг", 1000, gramm)

    ml = range_model("мл", 1)
    liter = range_model("литр", 1000, ml)

    # Действие и проверка
    with pytest.raises(operation_exception):
        kg.convert_to(liter, 5)


