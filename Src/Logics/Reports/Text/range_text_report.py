from Src.Logics.text_report import text_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class range_text_report(text_report):
    """
    Формирование текстового отчета по единице измерения.
    """

    def build(self, source: range_model) -> report_result_dto:
        """
        Сформировать текстовый отчёт для указанной единицы измерения.
        """
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        base_name = source.base_range.name if source.base_range else "Базовая"
        header_line = "Код | Наименование | Коэффициент | Базовая единица"
        data_line = f"{source.id} | {source.name} | {source.coefficient} | {base_name}"

        result = report_result_dto()
        result.text = f"{header_line}\n{data_line}"
        return result
