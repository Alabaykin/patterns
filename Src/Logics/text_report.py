from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class text_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате TXT
    """
    _handlers = {}

    @property
    def mimetype(self) -> str:
        return "text/plain; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        return False

    @property
    def file_extension(self) -> str:
        return "txt"

    def build(self, source: abstract_entity) -> report_result_dto:
        handler = self._handlers.get(type(source))
        if not handler:
            raise arguments_exception(f"Формирование текстового отчёта для типа '{type(source).__name__}' не поддерживается!")
        return handler().build(source)


class recipe_text_report(text_report):
    """
    Формирование текстового отчета по рецепту
    """
    def build(self, source: recipe_model) -> report_result_dto:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")

        header_line = "Код | Наименование | Брутто | Нетто"
        data_lines = [
            f"{item.nomenclature.id} | {item.nomenclature.name} | {item.gross} | {item.net}"
            for item in source.rows
        ]
        text = header_line
        if data_lines:
            text += "\n" + "\n".join(data_lines)

        result = report_result_dto()
        result.text = text
        return result


class nomenclature_text_report(text_report):
    """
    Формирование текстового отчета по номенклатуре
    """
    def build(self, source: nomenclature_model) -> report_result_dto:
        if not isinstance(source, nomenclature_model):
            raise arguments_exception("Источник данных должен быть объектом nomenclature_model")

        group_name = source.group.name if source.group else ""
        range_name = source.range.name if source.range else ""
        header_line = "Код | Краткое наименование | Полное наименование | Группа | Единица измерения"
        data_line = f"{source.id} | {source.name} | {source.full_name} | {group_name} | {range_name}"

        result = report_result_dto()
        result.text = f"{header_line}\n{data_line}"
        return result


class range_text_report(text_report):
    """
    Формирование текстового отчета по единице измерения
    """
    def build(self, source: range_model) -> report_result_dto:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")

        base_name = source.base_range.name if source.base_range else "Базовая"
        header_line = "Код | Наименование | Коэффициент | Базовая единица"
        data_line = f"{source.id} | {source.name} | {source.coefficient} | {base_name}"

        result = report_result_dto()
        result.text = f"{header_line}\n{data_line}"
        return result


text_report._handlers = {
    recipe_model: recipe_text_report,
    nomenclature_model: nomenclature_text_report,
    range_model: range_text_report,
}