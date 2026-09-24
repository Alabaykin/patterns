import pytest
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception

class test_entity(abstract_entity):
    pass

def test_abstract_entity_get_id_not_null():
    # Подготовка
    entity = test_entity()
    # Действие
    result = entity.id
    # Проверка
    assert result != ""

def test_abstract_entity_unique_ids():
    # Подготовка
    entity1 = test_entity()
    entity2 = test_entity()
    # Проверка
    assert entity1.id != entity2.id

def test_abstract_entity_same_id():
    # Подготовка
    entity1 = test_entity()
    entity2 = test_entity()
    entity1.id = "12"
    entity2.id = "12"

    # Проверка
    assert entity1 == entity2

def test_abstract_entity_set_empty_name():
    # Подготовка
    entity = test_entity()

    # Действие и проверка
    with pytest.raises(ValueError):
        entity.name = ""

def test_abstract_entity_set_empty_name_v2():
    # Подготовка
    entity = test_entity()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        entity.name = ""
