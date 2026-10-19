import html
from Src.Logics.html_report import html_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class range_html_report(html_report):
    """
    Формирование HTML-отчета по единице измерения.
    """

    def build(self, source: range_model) -> report_result_dto:
        """
        Сформировать HTML-отчёт для указанной единицы измерения.
        """
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        thead = "<thead><tr><th>Код</th><th>Наименование</th><th>Коэффициент</th><th>Базовая единица</th></tr></thead>"
        base_name = source.base_range.name if source.base_range else "Базовая"
        tr = f"<tr><td>{html.escape(str(source.id))}</td><td>{html.escape(source.name)}</td><td>{source.coefficient}</td><td>{html.escape(base_name)}</td></tr>"
        tbody = f"<tbody>\n{tr}\n</tbody>"
        body = f"<h2>Единица измерения: {html.escape(source.name)}</h2>\n<table border='1'>\n{thead}\n{tbody}\n</table>"
        full_html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Отчет</title></head>\n<body>\n{body}\n</body>\n</html>"

        result = report_result_dto()
        result.text = full_html
        return result
