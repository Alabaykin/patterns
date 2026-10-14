from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Core.exception import arguments_exception


"""
Реализация фабрики для построения отчётов
"""
class report_factory(abstract_report_factory):
    __mapping: dict[report_type_enum, type[abstract_report]]
    __settings: settings_model = None

    def __init__(self, settings: settings_model = None):
        self.__mapping = {
            report_type_enum.TXT: text_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report
        }
        if settings is not None:
            self.__settings = settings
        else:
            sm = settings_manager()
            if not sm.is_loaded:
                sm.load()
            self.__settings = sm.settings

    @property
    def settings(self) -> settings_model:
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        self.__settings = value

    def create(self, report_type: report_type_enum) -> abstract_report:
        if report_type not in self.__mapping:
            raise arguments_exception(f"Указанный тип отчета {report_type} не реализован!")

        report_class = self.__mapping[report_type]
        return report_class()

    def create_default(self) -> abstract_report:
        """
        Создает инстанс отчета на основе настроек response_format
        """
        format_name = "TXT"
        if self.__settings is not None and getattr(self.__settings, "response_format", None):
            format_name = self.__settings.response_format

        report_type = report_type_enum.from_string(format_name)
        if report_type is None:
            raise arguments_exception(f"Неизвестный формат в настройках: {format_name}")

        return self.create(report_type)
