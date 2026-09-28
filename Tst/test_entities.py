import pytest
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class test_entity(abstract_entity):
    """
    Тестовый класс-наследник abstract_entity для проверки базового функционала.
    """
    pass


def test_not_empty_id_after_instantiation_success():
    """
    У новой сущности должен быть сгенерирован непустой id.
    """
    # Подготовка
    entity = test_entity()

    # Действие
    result = entity.id

    # Проверка
    assert result != ""
    assert isinstance(result, str)


def test_unique_ids_for_different_instances_success():
    """
    У разных экземпляров сущности id должны различаться.
    """
    # Подготовка
    entity1 = test_entity()
    entity2 = test_entity()

    # Проверка
    assert entity1.id != entity2.id


def test_equality_with_same_id_success():
    """
    Сущности с одинаковым id считаются равными.
    """
    # Подготовка
    entity1 = test_entity()
    entity2 = test_entity()
    entity1.id = "12"
    entity2.id = "12"

    # Проверка
    assert entity1 == entity2


def test_raise_arguments_exception_when_set_empty_name():
    """
    При попытке задать пустое имя выбрасывается arguments_exception.
    """
    # Подготовка
    entity = test_entity()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        entity.name = ""


def test_raise_arguments_exception_when_set_empty_id():
    """
    При попытке задать пустой id выбрасывается arguments_exception.
    """
    # Подготовка
    entity = test_entity()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        entity.id = ""


def test_raise_arguments_exception_name_when_exceeds_max_length():
    """
    При попытке задать имя длиннее 50 символов выбрасывается arguments_exception.
    """
    # Подготовка
    entity = test_entity()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        entity.name = "a" * 51

