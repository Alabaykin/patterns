import pytest

from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Models.settings_model import settings_model


def test_success_report_factory_selects_format():
    """
    Фабрика создаёт построитель формата без передачи типа сущности.
    """
    for format_type, report_class in [
        (report_type_enum.TXT, text_report),
        (report_type_enum.MARKDOWN, markdown_report),
        (report_type_enum.CSV, csv_report),
        (report_type_enum.XML, xml_report),
        (report_type_enum.HTML, html_report),
    ]:
        # Подготовка
        factory = report_factory(settings_model())

        # Действие
        report = factory.create(format_type)

        # Проверка
        assert isinstance(report, abstract_report)
        assert type(report) is report_class


def test_raise_report_factory_unknown_format():
    """
    Неверный формат приводит к собственному исключению приложения.
    """
    for value in [None, 999, "CSV", []]:
        # Подготовка
        factory = report_factory(settings_model())

        # Действие и проверка
        with pytest.raises(arguments_exception):
            factory.create(value)


def test_success_report_factory_uses_current_injected_settings():
    """
    Изменение переданных настроек влияет на следующий create_default.
    """
    # Подготовка
    settings = settings_model()
    settings.response_format = report_type_enum.XML
    factory = report_factory(settings)

    # Действие
    first = factory.create_default()
    settings.response_format = report_type_enum.MARKDOWN
    second = factory.create_default()

    # Проверка
    assert factory.settings is settings
    assert isinstance(first, xml_report)
    assert isinstance(second, markdown_report)


def test_raise_report_factory_invalid_settings():
    """
    Фабрика проверяет явно переданную зависимость от настроек.
    """
    for value in [None, {}, "settings.json"]:
        # Подготовка
        settings = value

        # Действие и проверка
        with pytest.raises(arguments_exception):
            report_factory(settings)
