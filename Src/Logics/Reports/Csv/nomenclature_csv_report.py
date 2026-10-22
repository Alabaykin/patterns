from Src.Logics.csv_report import csv_report
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception


class nomenclature_csv_report(csv_report):
    """
    Формирование CSV-отчета по номенклатуре.
    """

    def build_header(self, source: nomenclature_model) -> str:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")
        return "Код;Краткое наименование;Полное наименование;Группа;Единица измерения"

    def build_body(self, source: nomenclature_model) -> str:
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        return f"{source.id};{source.name};{source.full_name};{group_name};{range_name}"
