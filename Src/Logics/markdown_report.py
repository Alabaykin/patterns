from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class markdown_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате Markdown
    """
    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/markdown; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return True

    @property
    def file_extension(self) -> str:
        return "md"

    def build(self, source: abstract_entity) -> report_result_dto:
        handler = self._handlers.get(type(source))
        if not handler:
            raise arguments_exception(f"Формирование Markdown-отчёта для типа '{type(source).__name__}' не поддерживается!")
        return handler().build(source)


class recipe_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по рецепту
    """
    def build(self, source: recipe_model) -> report_result_dto:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")

        header_line = "| Код | Наименование | Брутто | Нетто |"
        separator = "| :--- | :--- | :--- | :--- |"
        data_lines = [
            f"| {item.nomenclature.id} | {item.nomenclature.name} | {item.gross} | {item.net} |"
            for item in source.rows
        ]
        text = header_line + "\n" + separator
        if data_lines:
            text += "\n" + "\n".join(data_lines)

        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


class nomenclature_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по номенклатуре
    """
    def build(self, source: nomenclature_model) -> report_result_dto:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        header_line = "| Код | Краткое наименование | Полное наименование | Группа | Единица измерения |"
        separator = "| :--- | :--- | :--- | :--- | :--- |"
        data_line = f"| {source.id} | {source.name} | {source.full_name} | {group_name} | {range_name} |"
        text = f"{header_line}\n{separator}\n{data_line}"

        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


class range_markdown_report(markdown_report):
    """
    Формирование Markdown-отчета по единице измерения
    """
    def build(self, source: range_model) -> report_result_dto:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        base_name = source.base_range.name if source.base_range else "Базовая"
        header_line = "| Код | Наименование | Коэффициент | Базовая единица |"
        separator = "| :--- | :--- | :--- | :--- |"
        data_line = f"| {source.id} | {source.name} | {source.coefficient} | {base_name} |"
        text = f"{header_line}\n{separator}\n{data_line}"

        result = report_result_dto()
        result.binary = list(text.encode("utf-8"))
        return result


markdown_report._handlers = {
    recipe_model: recipe_markdown_report,
    nomenclature_model: nomenclature_markdown_report,
    range_model: range_markdown_report,
}
