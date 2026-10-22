import xml.etree.ElementTree as ET
from Src.Logics.xml_report import xml_report
from Src.Models.recipe_model import recipe_model
from Src.Core.exception import arguments_exception


class recipe_xml_report(xml_report):
    """
    Формирование XML-отчета по рецепту.
    """

    def build_body(self, source: recipe_model) -> str:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")

        root = ET.Element("recipe")
        name_el = ET.SubElement(root, "name")
        name_el.text = source.name

        rows_el = ET.SubElement(root, "rows")
        for item in source.rows:
            row_el = ET.SubElement(rows_el, "row")
            ET.SubElement(row_el, "code").text = str(item.nomenclature.id)
            ET.SubElement(row_el, "name").text = item.nomenclature.name
            ET.SubElement(row_el, "gross").text = str(item.gross)
            ET.SubElement(row_el, "net").text = str(item.net)

        return ET.tostring(root, encoding="unicode", xml_declaration=True)
