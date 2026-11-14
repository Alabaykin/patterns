import csv
from io import StringIO

from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.table_report import table_report


class csv_report(table_report):
    """CSV с единой схемой section;row;field;value для любых табличных частей."""

    @property
    def mimetype(self) -> str:
        """MIME-тип CSV."""
        return "text/csv"

    @property
    def file_extension(self) -> str:
        """Расширение CSV-файла."""
        return "csv"

    @property
    def is_attachment(self) -> bool:
        """CSV отдаётся скачиваемым файлом."""
        return True

    def _render(self, data: report_data_dto) -> str:
        """Записать все значения стандартным CSV writer с экранированием."""
        output = StringIO(newline="")
        writer = csv.writer(output, delimiter=";", lineterminator="\r\n")
        writer.writerow(["section", "row", "field", "value"])
        for field in data.fields:
            writer.writerow(["header", "", field.name, field.value])
        for table in data.tables:
            if not table.rows:
                writer.writerow([table.name, "", "", ""])
            for index, row in enumerate(table.rows, start=1):
                for name, value in zip(table.columns, row):
                    writer.writerow([table.name, index, name, value])
        return output.getvalue()
