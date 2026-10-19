from Src.Logics.text_report import text_report
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception
from Src.Models.recipe_model import recipe_model


class recipe_text_report(text_report):
    """
    Формирование текстового отчета по рецепту.
    """

    def build(self, source: recipe_model) -> report_result_dto:
        """
        Сформировать текстовый отчёт для указанного рецепта.
        """
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
