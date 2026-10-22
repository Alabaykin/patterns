from Src.Logics.csv_report import csv_report
from Src.Models.recipe_model import recipe_model
from Src.Core.exception import arguments_exception


class recipe_csv_report(csv_report):
    """
    Формирование CSV-отчета по рецепту.
    """

    def build_header(self, source: recipe_model) -> str:
        if not isinstance(source, recipe_model):
            raise arguments_exception("Источник данных должен быть объектом recipe_model")
        return "Код;Наименование;Брутто;Нетто"

    def build_body(self, source: recipe_model) -> str:
        lines = [
            f"{item.nomenclature.id};{item.nomenclature.name};{item.gross};{item.net}"
            for item in source.rows
        ]
        return "\n".join(lines)
