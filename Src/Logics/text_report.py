from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


class text_report(abstract_report):
    """
    Класс формирования отчёта в формате TXT
    """

    def build(self, source) -> report_result_dto:
        if isinstance(source, recipe_model):
            header = "Код | Наименование | Брутто | Нетто"
            data_rows = []
            for item in source.rows:
                data_rows.append(f"{item.nomenclature.id} | {item.nomenclature.name} | {item.gross} | {item.net}")
            text = f"{header}\n" + "\n".join(data_rows) if data_rows else header

        elif isinstance(source, nomenclature_model):
            group_name = source.group.name if source.group else ""
            range_name = source.range.name if source.range else ""
            text = (
                f"Код: {source.id}\n"
                f"Краткое наименование: {source.name}\n"
                f"Полное наименование: {source.full_name}\n"
                f"Группа: {group_name}\n"
                f"Единица измерения: {range_name}"
            )

        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else "Базовая"
            text = (
                f"Код: {source.id}\n"
                f"Наименование: {source.name}\n"
                f"Коэффициент: {source.coefficient}\n"
                f"Базовая единица: {base_name}"
            )

        else:
            raise arguments_exception(f"Неподдерживаемый тип источника данных: {type(source)}")

        result = report_result_dto()
        result.text = text
        return result