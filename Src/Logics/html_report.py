import html
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class html_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате HTML
    """
    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/html; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "html"

    def build(self, source: abstract_entity) -> report_result_dto:
        handler = self._handlers.get(type(source))
        if not handler:
            raise arguments_exception(f"Формирование HTML-отчёта для типа '{type(source).__name__}' не поддерживается!")
        return handler().build(source)


class recipe_html_report(html_report):
    """
    Формирование HTML-отчета по рецепту
    """
    def build(self, source: recipe_model) -> report_result_dto:
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


class nomenclature_html_report(html_report):
    """
    Формирование HTML-отчета по номенклатуре
    """
    def build(self, source: nomenclature_model) -> report_result_dto:
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


class range_html_report(html_report):
    """
    Формирование HTML-отчета по единице измерения
    """
    def build(self, source: range_model) -> report_result_dto:
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


html_report._handlers = {
    recipe_model: recipe_html_report,
    nomenclature_model: nomenclature_html_report,
    range_model: range_html_report,
}
