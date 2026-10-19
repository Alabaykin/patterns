import csv
import io
from Src.Logics.csv_report import csv_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class range_csv_report(csv_report):
    """
    Формирование CSV-отчета по единице измерения.
    """

    def build(self, source: range_model) -> report_result_dto:
        """
        Сформировать CSV-отчёт для указанной единицы измерения.
        """
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
