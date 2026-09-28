import pytest
from Src.Models.group_model import group_model
from Src.Core.exception import arguments_exception


def test_create_group_model_success():
    """
    Успешное создание модели группы номенклатуры.
    """
    # Действие
    group = group_model("Сырье")

    # Проверка
    assert group.name == "Сырье"
    assert group.id != ""


def test_raise_arguments_exception_when_group_name_is_empty():
    """
    Попытка создать группу с пустым именем вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        group_model("")


def test_raise_arguments_exception_when_group_name_exceeds_max_length():
    """
    Попытка создать группу с именем длиннее 50 символов вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        group_model("Г" * 51)
