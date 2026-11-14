from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Models.settings_model import settings_model
from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report


class report_factory(abstract_report_factory):
    """Выбирает построитель по формату; не знает типов доменных сущностей."""

    __mapping: dict[report_type_enum, type[abstract_report]] = {
        report_type_enum.TXT: text_report,
        report_type_enum.MARKDOWN: markdown_report,
        report_type_enum.CSV: csv_report,
        report_type_enum.XML: xml_report,
        report_type_enum.HTML: html_report,
    }

    def __init__(self, settings: settings_model):
        """Принять проверенные настройки через явную зависимость."""
        if not isinstance(settings, settings_model):
            raise arguments_exception("Ожидается модель настроек", "settings")
        self.__settings = settings

    @property
    def settings(self) -> settings_model:
        """Настройки, определяющие формат по умолчанию."""
        return self.__settings

    def create(self, report_type: report_type_enum) -> abstract_report:
        """Создать построитель выбранного формата."""
        if not isinstance(report_type, report_type_enum) or report_type not in self.__mapping:
            raise arguments_exception("Неизвестный формат отчёта", "report_type")
        return self.__mapping[report_type]()

    def create_default(self) -> abstract_report:
        """Создать построитель формата из настроек."""
        return self.create(self.__settings.response_format)
