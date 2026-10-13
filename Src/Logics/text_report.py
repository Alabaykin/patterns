from Src.Core.abstract_report import abstract_report
from Src.Models.recipe_model import recipe_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.validator import validator

class text_report(abstract_report):

    """
    Рецепт
    """
    __recipe: recipe_model

    """
    Метод формирования текстового отчёта
    """
    def build(self, source: recipe_model) -> report_result_dto:
        validator.validate(source, recipe_model)
        self.__recipe = source

        header = "Код | Наименование | Брутто | Нетто"

        data_rows = []
        for item in self.__recipe.rows:
            data_rows.append(f"{item.nomenclature.id} | {item.nomenclature.name} | {item.gross} | {item.net}")

        data = "\n".join(data_rows)
        result = report_result_dto()
        result.text = f"{header}\n{data}" if data else header
        return result