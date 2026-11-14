from Src.Core.validator import validator, operation_exception
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Dtos.report_type_enum import report_type_enum
import json
import pytest
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Core.exception import arguments_exception
from pathlib import Path

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
    assert settings.response_format == report_type_enum.MARKDOWN
    assert settings.format == report_type_enum.MARKDOWN



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


def test_success_settings_manager_common_deserialization():
    """
    Модель настроек поддерживает общую сериализацию и десериализацию.
    """
    # Подготовка
    manager = settings_manager()
    manager.load()
    payload = convert_factory().serialize(manager.settings)

    # Действие
    restored = deserialize_factory().deserialize(payload)

    # Проверка
    assert convert_factory().serialize(restored) == payload


def test_success_settings_manager_keeps_instance_and_optional_fields(tmp_path):
    """
    Прежний формат настроек сохраняет экземпляр, необязательные поля и значение false.
    """
    # Подготовка
    manager = settings_manager()
    manager.load()
    previous = manager.settings
    payload = json.loads((Path(__file__).resolve().parents[1] / "settings.json").read_text(encoding="utf-8"))
    payload.pop("boss_name")
    payload.pop("account_name")
    payload["is_first"] = False
    payload["response_format"] = "csv"
    path = tmp_path / "settings.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    try:
        # Действие
        manager.load(str(path))

        # Проверка
        assert manager.settings.is_first is False
        assert manager.settings.response_format == report_type_enum.CSV
        assert manager.settings is previous
        assert manager.settings.boss_name == "Иванов Иван Иванович"
        assert manager.settings.account_name == "Петров Петр Петрович"
        assert manager.settings.organization.name == payload["company_name"]
    finally:
        manager.load()


def test_raise_settings_manager_keeps_previous_settings_on_invalid_field(tmp_path):
    """
    Ошибка в любом поле не оставляет частично обновлённые настройки.
    """
    # Подготовка
    manager = settings_manager()
    manager.load()
    previous = manager.settings
    expected = convert_factory().serialize(previous)
    path = tmp_path / "bad_settings.json"
    cases = [("response_format", "pdf"), ("is_first", "false"), ("unknown", 1)]

    for field, value in cases:
        data = json.loads((Path(__file__).resolve().parents[1] / "settings.json").read_text(encoding="utf-8"))
        data["company_name"] = "Другая организация"
        data[field] = value
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        # Действие и проверка
        with pytest.raises(operation_exception):
            manager.load(str(path))
        assert manager.settings is previous
        assert manager.is_loaded is True
        assert convert_factory().serialize(previous) == expected


def test_raise_settings_manager_invalid_file_name_type():
    """
    Неверный тип имени файла приводит к собственному исключению до чтения.
    """
    # Подготовка
    manager = settings_manager()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        manager.load(None)
