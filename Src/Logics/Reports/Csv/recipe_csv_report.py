import csv
import io
from Src.Logics.csv_report import csv_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model


class recipe_csv_report(csv_report):
    """
    Формирование CSV-отчета по рецепту.
    """

    def build(self, source: recipe_model) -> report_result_dto:
        """
        Сформировать CSV-отчёт для указанного рецепта.
        """
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
