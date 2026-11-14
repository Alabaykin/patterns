from html import escape

from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.table_report import table_report


class html_report(table_report):
    """HTML-представление общих данных отчёта."""

    @property
    def mimetype(self) -> str:
        """MIME-тип HTML."""
        return "text/html"

    @property
    def file_extension(self) -> str:
        """Расширение HTML-файла."""
        return "html"

    def _render(self, data: report_data_dto) -> str:
        """Экранировать свойства, названия таблиц и каждую ячейку."""
        title = escape(data.title)
        parts = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'>",
            f"<title>{title}</title><style>td,dd {{white-space:pre-wrap}}</style></head><body><h1>{title}</h1><dl>",
        ]
        parts.extend(f"<dt>{escape(field.name)}</dt><dd>{escape(field.value)}</dd>" for field in data.fields)
        parts.append("</dl>")
        for table in data.tables:
            parts.append(f"<table><caption>{escape(table.name)}</caption><thead><tr>")
            parts.extend(f"<th>{escape(name)}</th>" for name in table.columns)
            parts.append("</tr></thead><tbody>")
            for row in table.rows:
                parts.append("<tr>" + "".join(f"<td>{escape(value)}</td>" for value in row) + "</tr>")
            parts.append("</tbody></table>")
        parts.append("</body></html>")
        return "".join(parts)
