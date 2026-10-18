import xml.etree.ElementTree as ET
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class xml_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате XML
    """
    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "application/xml; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "xml"

    def build(self, source: abstract_entity) -> report_result_dto:
        handler = self._handlers.get(type(source))
        if not handler:
            raise arguments_exception(f"Формирование XML-отчёта для типа '{type(source).__name__}' не поддерживается!")
        return handler().build(source)


class recipe_xml_report(xml_report):
    """
    Формирование XML-отчета по рецепту
    """
    def build(self, source: recipe_model) -> report_result_dto:
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

        xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
        result = report_result_dto()
        result.text = xml_text
        return result


class nomenclature_xml_report(xml_report):
    """
    Формирование XML-отчета по номенклатуре
    """
    def build(self, source: nomenclature_model) -> report_result_dto:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        root = ET.Element("nomenclature")
        ET.SubElement(root, "code").text = str(source.id)
        ET.SubElement(root, "name").text = source.name
        ET.SubElement(root, "full_name").text = source.full_name
        ET.SubElement(root, "group").text = source.group.name if source.group else ""
        ET.SubElement(root, "range").text = source.range.name if source.range else ""

        xml_text = ET.tostring(root, encoding="unicode", xml_declaration=True)
        result = report_result_dto()
        result.text = xml_text
        return result


class range_xml_report(xml_report):
    """
    Формирование XML-отчета по единице измерения
    """
    def build(self, source: range_model) -> report_result_dto:
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


xml_report._handlers = {
    recipe_model: recipe_xml_report,
    nomenclature_model: nomenclature_xml_report,
    range_model: range_xml_report,
}
