import xml.etree.ElementTree as ET

from Src.Dtos.report_data_dto import report_data_dto
from Src.Logics.table_report import table_report


class xml_report(table_report):
    """XML с общей схемой полей и таблиц, независимой от Python-имён свойств."""

    @property
    def mimetype(self) -> str:
        """MIME-тип XML."""
        return "application/xml"

    @property
    def file_extension(self) -> str:
        """Расширение XML-файла."""
        return "xml"

    def _render(self, data: report_data_dto) -> str:
        """Сформировать XML стандартным сериализатором с экранированием."""
        root = ET.Element("report", title=data.title)
        fields = ET.SubElement(root, "fields")
        for field in data.fields:
            ET.SubElement(fields, "field", name=field.name).text = field.value
        for table in data.tables:
            node = ET.SubElement(root, "table", name=table.name)
            columns = ET.SubElement(node, "columns")
            for name in table.columns:
                ET.SubElement(columns, "column").text = name
            for row in table.rows:
                row_node = ET.SubElement(node, "row")
                for name, value in zip(table.columns, row):
                    ET.SubElement(row_node, "cell", name=name).text = value
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
