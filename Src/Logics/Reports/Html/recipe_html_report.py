import html
from Src.Logics.html_report import html_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model


class recipe_html_report(html_report):
    """
    Формирование HTML-отчета по рецепту.
    """

    def build(self, source: recipe_model) -> report_result_dto:
        """
        Сформировать HTML-отчёт для указанного рецепта.
        """
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")

        thead = "<thead><tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr></thead>"
        tr_rows = [
            f"<tr><td>{html.escape(str(item.nomenclature.id))}</td><td>{html.escape(item.nomenclature.name)}</td><td>{item.gross}</td><td>{item.net}</td></tr>"
            for item in source.rows
        ]
        tbody = "<tbody>\n" + "\n".join(tr_rows) + "\n</tbody>"
        body = f"<h2>Рецепт: {html.escape(source.name)}</h2>\n<table border='1'>\n{thead}\n{tbody}\n</table>"
        full_html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Отчет</title></head>\n<body>\n{body}\n</body>\n</html>"

        result = report_result_dto()
        result.text = full_html
        return result
