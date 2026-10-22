from Src.Logics.html_report import html_report
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


class range_html_report(html_report):
    """
    Формирование HTML-отчета по единице измерения.
    """

    def build_header(self, source: range_model) -> str:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Единица измерения</title></head><body>"
            "<table border='1'><tr><th>Код</th><th>Наименование</th><th>Коэффициент</th><th>Базовая единица</th></tr>"
        )

    def build_body(self, source: range_model) -> str:
        base_name = source.base_range.name if source.base_range else "Базовая"
        return (
            f"<tr><td>{source.id}</td><td>{source.name}</td><td>{source.coefficient}</td>"
            f"<td>{base_name}</td></tr>"
        )

    def build_footer(self, source: range_model) -> str:
        return "</table></body></html>"
