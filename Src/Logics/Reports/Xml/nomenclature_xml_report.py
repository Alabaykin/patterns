import xml.etree.ElementTree as ET
from Src.Logics.xml_report import xml_report
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception


class nomenclature_xml_report(xml_report):
    """
    Формирование XML-отчета по номенклатуре.
    """

    def build_body(self, source: nomenclature_model) -> str:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        root = ET.Element("nomenclature")
        ET.SubElement(root, "code").text = str(source.id)
        ET.SubElement(root, "name").text = source.name
        ET.SubElement(root, "full_name").text = source.full_name
        ET.SubElement(root, "group").text = source.group.name if source.group else ""
        ET.SubElement(root, "range").text = source.range.name if source.range else ""

        return ET.tostring(root, encoding="unicode", xml_declaration=True)
