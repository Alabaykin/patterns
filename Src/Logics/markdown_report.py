from html import escape
import re

from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.table_report import table_report


class markdown_report(table_report):
    """Markdown-отчёт с экранированием значений и поддержкой нескольких таблиц."""

    @property
    def mimetype(self) -> str:
        """MIME-тип Markdown."""
        return "text/markdown"

    @property
    def file_extension(self) -> str:
        """Расширение Markdown-файла."""
        return "md"

    @property
    def is_attachment(self) -> bool:
        """Markdown отдаётся скачиваемым файлом."""
        return True

    @staticmethod
    def _escape(value: str) -> str:
        """Сохранить текст, исключив интерпретацию HTML и служебных символов Markdown."""
        value = escape(value, quote=False)
        value = re.sub(r"([\\\x60*_{}\[\]()#|])", r"\\\1", value)
        return value.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")

    def _render(self, data: report_data_dto) -> str:
        """Оформить заголовок и все строки каждой таблицы."""
        lines = [f"# {self._escape(data.title)}", ""]
        lines.extend(f"- {self._escape(field.name)}: {self._escape(field.value)}" for field in data.fields)
        for table in data.tables:
            lines.extend(["", f"## {self._escape(table.name)}", ""])
            if table.columns:
                lines.append("| " + " | ".join(self._escape(name) for name in table.columns) + " |")
                lines.append("| " + " | ".join("---" for name in table.columns) + " |")
                lines.extend("| " + " | ".join(self._escape(value) for value in row) + " |" for row in table.rows)
        return "\n".join(lines)
