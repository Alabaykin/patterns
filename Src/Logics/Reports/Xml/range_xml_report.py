import xml.etree.ElementTree as ET
from Src.Logics.xml_report import xml_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.range_model import range_model


class range_xml_report(xml_report):
    """
    Формирование XML-отчета по единице измерения.
    """

    def build(self, source: range_model) -> report_result_dto:
        """
        Сформировать XML-отчёт для указанной единицы измерения.
        """
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        root = ET.Element("range")
        ET.SubElement(root, "code").text = str(source.id)
        ET.SubElement(root, "name").text = source.name
        ET.SubElement(root, "coefficient").text = str(source.coefficient)
        ET.SubElement(root, "base_range").text = source.base_range.name if source.base_range else "Базовая"

        xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
        result = report_result_dto()
        result.text = xml_text
        return result
