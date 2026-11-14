from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.table_report import table_report


class text_report(table_report):
    """Текстовое представление свойств и всех таблиц произвольной модели."""

    @property
    def mimetype(self) -> str:
        """MIME-тип текстового отчёта."""
        return "text/plain"

    @property
    def file_extension(self) -> str:
        """Расширение текстового файла."""
        return "txt"

    def _render(self, data: report_data_dto) -> str:
        """Оформить свойства и таблицы без знания доменных типов."""
        lines = [data.title]
        lines.extend(f"{field.name}: {field.value}" for field in data.fields)
        for table in data.tables:
            lines.extend(["", f"[{table.name}]", " | ".join(table.columns)])
            lines.extend(" | ".join(row) for row in table.rows)
        return "\n".join(lines)
