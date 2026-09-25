import pytest
from Src.Models.warehouse_model import warehouse_model
from Src.Core.exception import arguments_exception


def test_create_warehouse_model_success():
    """
    Успешное создание модели склада.
    """
    # Действие
    warehouse = warehouse_model("Основной склад")

    # Проверка
    assert warehouse.name == "Основной склад"
    assert warehouse.id != ""


def test_raise_arguments_exception_when_warehouse_name_is_empty():
    """
    Попытка создать склад с пустым именем вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        warehouse_model("")


def test_raise_arguments_exception_when_warehouse_name_exceeds_max_length():
    """
    Попытка создать склад с именем длиннее 50 символов вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        warehouse_model("С" * 51)
