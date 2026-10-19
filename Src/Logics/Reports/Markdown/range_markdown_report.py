from Src.Logics.markdown_report import markdown_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class range_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по единице измерения.
    """

    def build(self, source: range_model) -> report_result_dto:
        """
        Сформировать Markdown-отчёт для указанной единицы измерения.
        """
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        base_name = source.base_range.name if source.base_range else "Базовая"
        header_line = "| Код | Наименование | Коэффициент | Базовая единица |"
        separator = "| :--- | :--- | :--- | :--- |"
        data_line = f"| {source.id} | {source.name} | {source.coefficient} | {base_name} |"
        text = f"{header_line}\n{separator}\n{data_line}"

        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result
