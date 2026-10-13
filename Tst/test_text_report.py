import pytest
from Src.Logics.text_report import text_report
from Src.Models.recipe_model import recipe_model
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


def test_text_report_build_success():
    """
    Проверка успешного формирования текстового отчета по рецепту.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    report = text_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert isinstance(result.text, str)
    assert len(result.text) > 0
    assert result.binary == []

    lines = result.text.split("\n")
    assert lines[0] == "Код | Наименование | Брутто | Нетто"
    assert len(lines) == len(recipe.rows) + 1


