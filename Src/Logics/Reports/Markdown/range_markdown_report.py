from Src.Logics.markdown_report import markdown_report
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


class range_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по единице измерения.
    """

    def build_header(self, source: range_model) -> str:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")
        header_line = "| Код | Наименование | Коэффициент | Базовая единица |"
        separator = "| :--- | :--- | :--- | :--- |"
        return f"{header_line}\n{separator}"

    def build_body(self, source: range_model) -> str:
        base_name = source.base_range.name if source.base_range else "Базовая"
        return f"| {source.id} | {source.name} | {source.coefficient} | {base_name} |"
