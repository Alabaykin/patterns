from Src.Logics.markdown_report import markdown_report
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception


class nomenclature_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по номенклатуре.
    """

    def build_header(self, source: nomenclature_model) -> str:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")
        header_line = "| Код | Краткое наименование | Полное наименование | Группа | Единица измерения |"
        separator = "| :--- | :--- | :--- | :--- | :--- |"
        return f"{header_line}\n{separator}"

    def build_body(self, source: nomenclature_model) -> str:
        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        return f"| {source.id} | {source.name} | {source.full_name} | {group_name} | {range_name} |"
