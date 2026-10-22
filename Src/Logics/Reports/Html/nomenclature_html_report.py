from Src.Logics.html_report import html_report
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception


class nomenclature_html_report(html_report):
    """
    Формирование HTML-отчета по номенклатуре.
    """

    def build_header(self, source: nomenclature_model) -> str:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Номенклатура</title></head><body>"
            "<table border='1'><tr><th>Код</th><th>Краткое наименование</th><th>Полное наименование</th>"
            "<th>Группа</th><th>Единица измерения</th></tr>"
        )

    def build_body(self, source: nomenclature_model) -> str:
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        return (
            f"<tr><td>{source.id}</td><td>{source.name}</td><td>{source.full_name}</td>"
            f"<td>{group_name}</td><td>{range_name}</td></tr>"
        )

    def build_footer(self, source: nomenclature_model) -> str:
        return "</table></body></html>"
