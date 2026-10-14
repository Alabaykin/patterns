import csv
import io
from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


class csv_report(abstract_report):
    """
    Класс формирования отчёта в формате CSV
    """

    def build(self, source) -> report_result_dto:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", lineterminator="\n")

        if isinstance(source, recipe_model):
            writer.writerow(["Код", "Наименование", "Брутто", "Нетто"])
            for item in source.rows:
                writer.writerow([item.nomenclature.id, item.nomenclature.name, item.gross, item.net])

        elif isinstance(source, nomenclature_model):
            writer.writerow(["Код", "Краткое наименование", "Полное наименование", "Группа", "Единица измерения"])
            group_name = source.group.name if source.group else ""
            range_name = source.range.name if source.range else ""
            writer.writerow([source.id, source.name, source.full_name, group_name, range_name])

        elif isinstance(source, range_model):
            writer.writerow(["Код", "Наименование", "Коэффициент", "Базовая единица"])
            base_name = source.base_range.name if source.base_range else "Базовая"
            writer.writerow([source.id, source.name, source.coefficient, base_name])

        else:
            raise arguments_exception(f"Неподдерживаемый тип источника данных: {type(source)}")

        text = output.getvalue()
        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result
