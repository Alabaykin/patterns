from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.validator import validator
from Src.Core.exception import arguments_exception


class markdown_report(abstract_report):
    """
    Класс формирования отчёта в формате Markdown
    """

    def build(self, source) -> report_result_dto:
        if isinstance(source, recipe_model):
            header = "| Код | Наименование | Брутто | Нетто |\n| :--- | :--- | :--- | :--- |"
            rows = []
            for item in source.rows:
                rows.append(f"| {item.nomenclature.id} | {item.nomenclature.name} | {item.gross} | {item.net} |")
            text = f"{header}\n" + "\n".join(rows) if rows else header

        elif isinstance(source, nomenclature_model):
            header = "| Поле | Значение |\n| :--- | :--- |"
            rows = [
                f"| Код | {source.id} |",
                f"| Краткое наименование | {source.name} |",
                f"| Полное наименование | {source.full_name} |",
                f"| Группа | {source.group.name if source.group else ''} |",
                f"| Единица измерения | {source.range.name if source.range else ''} |"
            ]
            text = f"{header}\n" + "\n".join(rows)

        elif isinstance(source, range_model):
            header = "| Поле | Значение |\n| :--- | :--- |"
            base_name = source.base_range.name if source.base_range else "Базовая"
            rows = [
                f"| Код | {source.id} |",
                f"| Наименование | {source.name} |",
                f"| Коэффициент | {source.coefficient} |",
                f"| Базовая единица | {base_name} |"
            ]
            text = f"{header}\n" + "\n".join(rows)

        else:
            raise arguments_exception(f"Неподдерживаемый тип источника данных: {type(source)}")

        result = report_result_dto()
        binary_data = list(text.encode("utf-8"))
        result.binary = binary_data
        return result
