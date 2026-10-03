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


"""
Проверить корректность конвертации данных в поля модели settings_model
"""
def test_convert_fields_settings_manager_success():
    # Подготовка
    manager = settings_manager()

    # Действие
    manager.load()

    # Проверка
    settings = manager.settings
    assert settings is not None
    assert settings.boss_name == "Иванов Иван Иванович"
    assert settings.account_name == "Петров Петр Петрович"
    assert settings.organization is not None
    assert settings.organization.name == "ООО Ромашка"
    assert settings.organization.inn == "1234567890"
    assert settings.organization.bik == "123456789"
    assert settings.organization.account == "12345678901234567890"
    assert settings.organization.ownership_type == "ООО"
    assert isinstance(settings.is_first, bool)



"""
Проверить, что настройки двух разных инстансов settings_manager совпадают (Singleton)
"""
def test_equals_settings_across_instances():
    # Подготовка
    manager1 = settings_manager()
    manager2 = settings_manager()

    # Действие
    manager1.load()

    # Проверка
    assert manager1.settings is manager2.settings



"""
Проверить выброс исключения operation_exception при загрузке несуществующего файла
"""
def test_raise_operation_exception_on_missing_file():
    manager = settings_manager()
    try:
        manager.load("non_existent_file_path_12345.json")
        assert False
    except operation_exception:
        assert True
    except:
        assert False