from Src.Logics.text_report import text_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model


class nomenclature_text_report(text_report):
    """
    Формирование текстового отчета по номенклатуре.
    """

    def build(self, source: nomenclature_model) -> report_result_dto:
        """
        Сформировать текстовый отчёт для указанной номенклатуры.
        """
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        header_line = "Код | Краткое наименование | Полное наименование | Группа | Единица измерения"
        data_line = f"{source.id} | {source.name} | {source.full_name} | {group_name} | {range_name}"

        result = report_result_dto()
        result.text = f"{header_line}\n{data_line}"
        return result
