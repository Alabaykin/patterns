from Src.Logics.html_report import html_report
from Src.Models.recipe_model import recipe_model
from Src.Core.exception import arguments_exception


class recipe_html_report(html_report):
    """
    Формирование HTML-отчета по рецепту.
    """

    def build_header(self, source: recipe_model) -> str:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Рецепт</title></head><body>"
            f"<h1>{source.name}</h1>"
            "<table border='1'><tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr>"
        )

    def build_body(self, source: recipe_model) -> str:
        rows = [
            f"<tr><td>{item.nomenclature.id}</td><td>{item.nomenclature.name}</td>"
            f"<td>{item.gross}</td><td>{item.net}</td></tr>"
            for item in source.rows
        ]
        return "".join(rows)

    def build_footer(self, source: recipe_model) -> str:
        return "</table></body></html>"
