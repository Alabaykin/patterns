from Src.Logics.text_report import text_report
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception


class nomenclature_text_report(text_report):
    """
    Формирование текстового отчета по номенклатуре.
    """

    def build_header(self, source: nomenclature_model) -> str:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")
        return "Номенклатура\nКод | Краткое наименование | Полное наименование | Группа | Единица измерения\n" + "-" * 80

    def build_body(self, source: nomenclature_model) -> str:
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        return f"{source.id} | {source.name} | {source.full_name} | {group_name} | {range_name}"
