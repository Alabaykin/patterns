import csv
import io
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class csv_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате CSV
    """
    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/csv; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "csv"

    def build(self, source: abstract_entity) -> report_result_dto:
        handler = self._handlers.get(type(source))
        if not handler:
            raise arguments_exception(f"Формирование CSV-отчёта для типа '{type(source).__name__}' не поддерживается!")
        return handler().build(source)


class recipe_csv_report(csv_report):
    """
    Формирование CSV-отчета по рецепту
    """
    def build(self, source: recipe_model) -> report_result_dto:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", lineterminator="\n")
        writer.writerow(["Код", "Наименование", "Брутто", "Нетто"])
        for item in source.rows:
            writer.writerow([item.nomenclature.id, item.nomenclature.name, item.gross, item.net])

        text = output.getvalue()
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


class nomenclature_csv_report(csv_report):
    """
    Формирование CSV-отчета по номенклатуре
    """
    def build(self, source: nomenclature_model) -> report_result_dto:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", lineterminator="\n")
        writer.writerow(["Код", "Краткое наименование", "Полное наименование", "Группа", "Единица измерения"])
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        writer.writerow([source.id, source.name, source.full_name, group_name, range_name])

        text = output.getvalue()
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


class range_csv_report(csv_report):
    """
    Формирование CSV-отчета по единице измерения
    """
    def build(self, source: range_model) -> report_result_dto:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", lineterminator="\n")
        writer.writerow(["Код", "Наименование", "Коэффициент", "Базовая единица"])
        base_name = source.base_range.name if source.base_range else "Базовая"
        writer.writerow([source.id, source.name, source.coefficient, base_name])

        text = output.getvalue()
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


csv_report._handlers = {
    recipe_model: recipe_csv_report,
    nomenclature_model: nomenclature_csv_report,
    range_model: range_csv_report,
}
