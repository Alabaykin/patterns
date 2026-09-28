import pytest
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def default_group():
    return group_model("Сырье")


@pytest.fixture
def default_range():
    return range_model("кг", 1000)


def test_create_nomenclature_success(default_group, default_range):
    """
    Успешное создание номенклатуры со всеми корректными параметрами.
    """
    # Действие
    item = nomenclature_model(
        name="Мука пшеничная",
        full_name="Мука пшеничная высший сорт ГОСТ 26574-2017",
        group=default_group,
        range=default_range
    )

    # Проверка
    assert item.name == "Мука пшеничная"
    assert item.full_name == "Мука пшеничная высший сорт ГОСТ 26574-2017"
    assert item.group == default_group
    assert item.range == default_range
    assert item.id != ""


def test_raise_arguments_exception_when_name_exceeds_max_length(default_group, default_range):
    """
    Попытка задать краткое наименование длиннее 50 символов вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        nomenclature_model(
            name="М" * 51,
            full_name="Мука пшеничная",
            group=default_group,
            range=default_range
        )


def test_raise_arguments_exception_when_full_name_is_empty(default_group, default_range):
    """
    Попытка задать пустое полное наименование вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        nomenclature_model(
            name="Мука",
            full_name="",
            group=default_group,
            range=default_range
        )


def test_raise_arguments_exception_when_full_name_exceeds_max_length(default_group, default_range):
    """
    Попытка задать полное наименование длиннее 255 символов вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        nomenclature_model(
            name="Мука",
            full_name="М" * 256,
            group=default_group,
            range=default_range
        )


def test_raise_arguments_exception_when_group_is_invalid_type(default_range):
    """
    Попытка передать некорректный объект вместо group_model вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        nomenclature_model(
            name="Мука",
            full_name="Мука пшеничная",
            group="не group_model",
            range=default_range
        )


def test_raise_arguments_exception_when_range_is_invalid_type(default_group):
    """
    Попытка передать некорректный объект вместо range_model вызывает arguments_exception.
    """
    with pytest.raises(arguments_exception):
        nomenclature_model(
            name="Мука",
            full_name="Мука пшеничная",
            group=default_group,
            range="не range_model"
        )
