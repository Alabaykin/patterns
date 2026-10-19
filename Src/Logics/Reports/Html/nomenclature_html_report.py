import html
from Src.Logics.html_report import html_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_html_report(html_report):
    """
    Формирование HTML-отчета по номенклатуре.
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        """
        Сформировать HTML-отчёт для указанной номенклатуры.
        """
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        thead = "<thead><tr><th>Код</th><th>Краткое наименование</th><th>Полное наименование</th><th>Группа</th><th>Единица измерения</th></tr></thead>"
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        tr = f"<tr><td>{html.escape(str(source.id))}</td><td>{html.escape(source.name)}</td><td>{html.escape(source.full_name)}</td><td>{html.escape(group_name)}</td><td>{html.escape(range_name)}</td></tr>"
        tbody = f"<tbody>\n{tr}\n</tbody>"
        body = f"<h2>Номенклатура: {html.escape(source.name)}</h2>\n<table border='1'>\n{thead}\n{tbody}\n</table>"
        full_html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Отчет</title></head>\n<body>\n{body}\n</body>\n</html>"

        result = report_result_dto()
        result.text = full_html
        return result
