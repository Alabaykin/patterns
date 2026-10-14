import xml.etree.ElementTree as ET
from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


class xml_report(abstract_report):
    """
    Класс формирования отчёта в формате XML
    """

    def build(self, source) -> report_result_dto:
        if isinstance(source, recipe_model):
            root = ET.Element("recipe")
            ET.SubElement(root, "id").text = str(source.id)
            ET.SubElement(root, "name").text = str(source.name)
            rows_el = ET.SubElement(root, "rows")
            for item in source.rows:
                row_el = ET.SubElement(rows_el, "row")
                ET.SubElement(row_el, "id").text = str(item.nomenclature.id)
                ET.SubElement(row_el, "name").text = str(item.nomenclature.name)
                ET.SubElement(row_el, "gross").text = str(item.gross)
                ET.SubElement(row_el, "net").text = str(item.net)

        elif isinstance(source, nomenclature_model):
            root = ET.Element("nomenclature")
            ET.SubElement(root, "id").text = str(source.id)
            ET.SubElement(root, "name").text = str(source.name)
            ET.SubElement(root, "full_name").text = str(source.full_name)
            ET.SubElement(root, "group").text = str(source.group.name if source.group else "")
            ET.SubElement(root, "range").text = str(source.range.name if source.range else "")

        elif isinstance(source, range_model):
            root = ET.Element("range")
            ET.SubElement(root, "id").text = str(source.id)
            ET.SubElement(root, "name").text = str(source.name)
            ET.SubElement(root, "coefficient").text = str(source.coefficient)
            base_name = source.base_range.name if source.base_range else "Базовая"
            ET.SubElement(root, "base_range").text = str(base_name)

        else:
            raise arguments_exception(f"Неподдерживаемый тип источника данных: {type(source)}")

        xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
        result = report_result_dto()
        result.text = xml_text
        return result
