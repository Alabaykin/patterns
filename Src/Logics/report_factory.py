from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.settings_manager import settings_manager
from Src.Models.settings_model import settings_model
from Src.Core.exception import arguments_exception

from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report

from Src.Logics.Reports.Text.recipe_text_report import recipe_text_report
from Src.Logics.Reports.Text.nomenclature_text_report import nomenclature_text_report
from Src.Logics.Reports.Text.range_text_report import range_text_report

from Src.Logics.Reports.Markdown.recipe_markdown_report import recipe_markdown_report
from Src.Logics.Reports.Markdown.nomenclature_markdown_report import nomenclature_markdown_report
from Src.Logics.Reports.Markdown.range_markdown_report import range_markdown_report

from Src.Logics.Reports.Csv.recipe_csv_report import recipe_csv_report
from Src.Logics.Reports.Csv.nomenclature_csv_report import nomenclature_csv_report
from Src.Logics.Reports.Csv.range_csv_report import range_csv_report

from Src.Logics.Reports.Xml.recipe_xml_report import recipe_xml_report
from Src.Logics.Reports.Xml.nomenclature_xml_report import nomenclature_xml_report
from Src.Logics.Reports.Xml.range_xml_report import range_xml_report

from Src.Logics.Reports.Html.recipe_html_report import recipe_html_report
from Src.Logics.Reports.Html.nomenclature_html_report import nomenclature_html_report
from Src.Logics.Reports.Html.range_html_report import range_html_report


class report_factory(abstract_report_factory):
    """
    Реализация фабрики для построения отчётов.
    Инкапсулирует создание как базовых генераторов отчетов по формату,
    так и специализированных генераторов по паре (формат, сущность).
    """
    __settings: settings_model = None

    def __init__(self, settings: settings_model = None):
        """
        Инициализация фабрики отчетов с инкапсуляцией настроек.
        """
        self.__specialized_mapping: dict[tuple[report_type_enum, str], type[abstract_report]] = {
            (report_type_enum.TXT, "recipe"): recipe_text_report,
            (report_type_enum.TXT, "nomenclature"): nomenclature_text_report,
            (report_type_enum.TXT, "range"): range_text_report,

            (report_type_enum.CSV, "recipe"): recipe_csv_report,
            (report_type_enum.CSV, "nomenclature"): nomenclature_csv_report,
            (report_type_enum.CSV, "range"): range_csv_report,

            (report_type_enum.MARKDOWN, "recipe"): recipe_markdown_report,
            (report_type_enum.MARKDOWN, "nomenclature"): nomenclature_markdown_report,
            (report_type_enum.MARKDOWN, "range"): range_markdown_report,

            (report_type_enum.XML, "recipe"): recipe_xml_report,
            (report_type_enum.XML, "nomenclature"): nomenclature_xml_report,
            (report_type_enum.XML, "range"): range_xml_report,

            (report_type_enum.HTML, "recipe"): recipe_html_report,
            (report_type_enum.HTML, "nomenclature"): nomenclature_html_report,
            (report_type_enum.HTML, "range"): range_html_report,
        }

        self.__format_mapping: dict[report_type_enum, type[abstract_report]] = {
            report_type_enum.TXT: text_report,
            report_type_enum.MARKDOWN: markdown_report,
            report_type_enum.CSV: csv_report,
            report_type_enum.XML: xml_report,
            report_type_enum.HTML: html_report,
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
        """
        Инкапсулированные настройки приложения.
        """
        return self.__settings

    @settings.setter
    def settings(self, value: settings_model) -> None:
        """
        Установка инкапсулированных настроек приложения.
        """
        self.__settings = value

    @staticmethod
    def normalize_entity_type(entity_type) -> str:
        """
        Нормализация наименования типа сущности.
        Поддерживает строку, тип класса или экземпляр сущности.
        """
        if isinstance(entity_type, abstract_entity):
            entity_type = type(entity_type).__name__
        elif isinstance(entity_type, type):
            entity_type = entity_type.__name__
        elif not isinstance(entity_type, str):
            return ""

        norm = entity_type.strip().lower()
        aliases = {
            "recipe_model": "recipe",
            "рецепт": "recipe",
            "nomenclature_model": "nomenclature",
            "номенклатура": "nomenclature",
            "range_model": "range",
            "единица_измерения": "range",
            "единица измерения": "range",
            "единица": "range",
            "unit": "range",
        }
        return aliases.get(norm, norm)

    def create(self, report_type: report_type_enum, entity_type = "") -> abstract_report:
        """
        Создать экземпляр отчета заданного формата и, опционально, сущности.
        """
        if not isinstance(report_type, report_type_enum):
            raise arguments_exception(f"Указанный тип отчета {report_type} не реализован!")

        if entity_type:
            norm_entity = self.normalize_entity_type(entity_type)
            key = (report_type, norm_entity)
            if key in self.__specialized_mapping:
                return self.__specialized_mapping[key]()
            raise arguments_exception(f"Формирование отчёта {report_type.name} для сущности '{entity_type}' не поддерживается!")

        if report_type not in self.__format_mapping:
            raise arguments_exception(f"Указанный тип отчета {report_type} не реализован!")

        report_class = self.__format_mapping[report_type]
        return report_class()

    def create_default(self, entity_type = "") -> abstract_report:
        """
        Создает инстанс отчета на основе настроек response_format.
        """
        fmt = report_type_enum.TXT
        if self.__settings is not None:
            fmt = self.__settings.response_format

        return self.create(fmt, entity_type)
