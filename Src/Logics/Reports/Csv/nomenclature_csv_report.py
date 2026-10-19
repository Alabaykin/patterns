import csv
import io
from Src.Logics.csv_report import csv_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_csv_report(csv_report):
    """
    Формирование CSV-отчета по номенклатуре.
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        """
        Сформировать CSV-отчёт для указанной номенклатуры.
        """
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
