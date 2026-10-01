from Src.Core.validator import validator, operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model

"""
Набор модульных тестов для класса settings_manager
"""
def test_not_raise_settings_manager_load():
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    try:
        manager.load()

    except operation_exception:
        assert False

    except:
        assert False



"""
Проверить загрузку настроек. Настройки не пустые
"""
def test_not_empty_settings_manager_load():
    # Подготовка
    manager = settings_manager()
    
    # Действие и проверка
    try:
        manager.load()    
    except:
        assert False

    # Проверка
    assert manager.settings is not None


"""
Проверить работу шаблока Singletone
"""
def test_equall_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()

    # Действие
    instance2 = settings_manager()

    # Проверка
    assert instance1 == instance2


"""
Проверить загрузку и конвертацию настроек.
"""
def test_is_loaded_settings_manager_true():
    # Подготовка
    manager = settings_manager()

    # Действие
    try:
        manager.load()
    except:
        assert False

    # Проверка
    assert manager.is_loaded == True


"""
Проверить создание settings_manager: одинаковые строки и ссылки (Singletone)
"""
def test_same_strings_settings_manager_create():
    # Подготовка
    instance1 = settings_manager()

    # Действие
    instance2 = settings_manager()

    # Действие и проверка
    try:
        # Проверка одинаковых строк строкового представления
        assert str(instance1) == str(instance2)
        # Проверка одинаковых ссылок на объект
        assert instance1 is instance2
    except:
        assert False