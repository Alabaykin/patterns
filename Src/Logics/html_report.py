import html
from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


class html_report(abstract_report):
    """
    Класс формирования отчёта в формате HTML 
    """

    def build(self, source) -> report_result_dto:
        if isinstance(source, recipe_model):
            rows_html = []
            for item in source.rows:
                rows_html.append(
                    f"<tr><td>{html.escape(str(item.nomenclature.id))}</td>"
                    f"<td>{html.escape(str(item.nomenclature.name))}</td>"
                    f"<td>{html.escape(str(item.gross))}</td>"
                    f"<td>{html.escape(str(item.net))}</td></tr>"
                )
            body = (
                f"<h2>Рецепт: {html.escape(str(source.name))} (ID: {html.escape(str(source.id))})</h2>\n"
                f"<table border='1'><thead><tr><th>Код</th><th>Наименование</th><th>Брутто</th><th>Нетто</th></tr></thead>\n"
                f"<tbody>\n" + "\n".join(rows_html) + "\n</tbody></table>"
            )

        elif isinstance(source, nomenclature_model):
            group_name = source.group.name if source.group else ""
            range_name = source.range.name if source.range else ""
            body = (
                f"<h2>Номенклатура: {html.escape(str(source.name))}</h2>\n"
                f"<table border='1'>\n"
                f"<tr><th>Код</th><td>{html.escape(str(source.id))}</td></tr>\n"
                f"<tr><th>Краткое наименование</th><td>{html.escape(str(source.name))}</td></tr>\n"
                f"<tr><th>Полное наименование</th><td>{html.escape(str(source.full_name))}</td></tr>\n"
                f"<tr><th>Группа</th><td>{html.escape(str(group_name))}</td></tr>\n"
                f"<tr><th>Единица измерения</th><td>{html.escape(str(range_name))}</td></tr>\n"
                f"</table>"
            )

        elif isinstance(source, range_model):
            base_name = source.base_range.name if source.base_range else "Базовая"
            body = (
                f"<h2>Единица измерения: {html.escape(str(source.name))}</h2>\n"
                f"<table border='1'>\n"
                f"<tr><th>Код</th><td>{html.escape(str(source.id))}</td></tr>\n"
                f"<tr><th>Наименование</th><td>{html.escape(str(source.name))}</td></tr>\n"
                f"<tr><th>Коэффициент</th><td>{html.escape(str(source.coefficient))}</td></tr>\n"
                f"<tr><th>Базовая единица</th><td>{html.escape(str(base_name))}</td></tr>\n"
                f"</table>"
            )

        else:
            raise arguments_exception(f"Неподдерживаемый тип источника данных: {type(source)}")

        full_html = f"<!DOCTYPE html>\n<html>\n<head><meta charset='utf-8'><title>Отчет</title></head>\n<body>\n{body}\n</body>\n</html>"
        result = report_result_dto()
        result.text = full_html
        return result
