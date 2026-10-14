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


def test_text_report_build_nomenclature():
    """
    Проверка формирования текстового отчета по номенклатуре.
    """
    from Src.Models.nomenclature_model import nomenclature_model

    nom = nomenclature_model.create_flour()
    report = text_report()

    result = report.build(nom)
    assert isinstance(result, report_result_dto)
    assert f"Код: {nom.id}" in result.text
    assert f"Краткое наименование: {nom.name}" in result.text
    assert f"Полное наименование: {nom.full_name}" in result.text


def test_text_report_build_range():
    """
    Проверка формирования текстового отчета по единице измерения.
    """
    from Src.Models.range_model import range_model

    unit = range_model.create_kilogramm()
    report = text_report()

    result = report.build(unit)
    assert isinstance(result, report_result_dto)
    assert f"Код: {unit.id}" in result.text
    assert f"Наименование: {unit.name}" in result.text
    assert f"Коэффициент: {unit.coefficient}" in result.text



