import pytest
from Src.Models.organization_model import organization_model
from Src.Core.exception import arguments_exception


def test_create_organization_with_10_digit_inn_success():
    """
    Успешное создание организации с 10-значным ИНН (юрлицо).
    """
    # Действие
    org = organization_model(
        name="ООО Ромашка",
        inn="1234567890",
        bik="123456789",
        account="12345678901234567890",
        ownership_type="ООО"
    )

    # Проверка
    assert org.name == "ООО Ромашка"
    assert org.inn == "1234567890"
    assert org.bik == "123456789"
    assert org.account == "12345678901234567890"
    assert org.ownership_type == "ООО"
    assert org.id != ""


def test_create_organization_with_12_digit_inn_success():
    """
    Успешное создание организации с 12-значным ИНН (ИП).
    """
    # Действие
    org = organization_model(
        name="ИП Иванов",
        inn="123456789012",
        bik="123456789",
        account="12345678901234567890",
        ownership_type="ИП"
    )

    # Проверка
    assert org.inn == "123456789012"


def test_raise_arguments_exception_when_inn_has_invalid_length():
    """
    Попытка задать ИНН неверной длины (например, 11 цифр) вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="12345678901",
            bik="123456789",
            account="12345678901234567890",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_inn_contains_non_digits():
    """
    Попытка задать ИНН с буквами вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="12345abc90",
            bik="123456789",
            account="12345678901234567890",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_bik_has_invalid_length():
    """
    Попытка задать БИК не из 9 цифр вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="12345",
            account="12345678901234567890",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_bik_contains_non_digits():
    """
    Попытка задать БИК с буквами вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="12345678a",
            account="12345678901234567890",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_account_has_invalid_length():
    """
    Попытка задать счет не из 20 цифр вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="123456789",
            account="12345",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_account_contains_non_digits():
    """
    Попытка задать счет с буквами вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="123456789",
            account="1234567890123456789a",
            ownership_type="ООО"
        )


def test_raise_arguments_exception_when_ownership_type_is_empty():
    """
    Попытка задать пустую форму собственности вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="123456789",
            account="12345678901234567890",
            ownership_type=""
        )


def test_raise_arguments_exception_when_ownership_type_exceeds_max_length():
    """
    Попытка задать форму собственности длиннее 50 символов вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        organization_model(
            name="ООО Тест",
            inn="1234567890",
            bik="123456789",
            account="12345678901234567890",
            ownership_type="Ф" * 51
        )
