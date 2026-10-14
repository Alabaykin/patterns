import pytest
from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Models.recipe_model import recipe_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Dtos.report_result_dto import report_result_dto


@pytest.fixture
def recipe():
    return recipe_model.create_dough_recipe()


@pytest.fixture
def nomenclature():
    return nomenclature_model.create_flour()


@pytest.fixture
def range_item():
    return range_model.create_kilogramm()


def test_markdown_report_recipe(recipe):
    """
    Проверка формирования отчета Markdown для рецепта.
    """
    # Подготовка
    report = markdown_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    text = bytes(result.binary).decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in text
    for r in recipe.rows:
        assert r.nomenclature.name in text


def test_markdown_report_nomenclature(nomenclature):
    """
    Проверка формирования отчета Markdown для номенклатуры.
    """
    # Подготовка
    report = markdown_report()

    # Действие
    result = report.build(nomenclature)

    # Проверка
    text = bytes(result.binary).decode("utf-8")
    assert "| Поле | Значение |" in text
    assert nomenclature.name in text
    assert nomenclature.full_name in text


def test_markdown_report_range(range_item):
    """
    Проверка формирования отчета Markdown для единицы измерения.
    """
    # Подготовка
    report = markdown_report()

    # Действие
    result = report.build(range_item)

    # Проверка
    text = bytes(result.binary).decode("utf-8")
    assert range_item.name in text


def test_csv_report_recipe(recipe):
    """
    Проверка формирования отчета CSV для рецепта.
    """
    # Подготовка
    report = csv_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.binary) > 0
    text = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Брутто;Нетто" in text
    for r in recipe.rows:
        assert r.nomenclature.name in text


def test_csv_report_nomenclature(nomenclature):
    """
    Проверка формирования отчета CSV для номенклатуры.
    """
    # Подготовка
    report = csv_report()

    # Действие
    result = report.build(nomenclature)

    # Проверка
    text = bytes(result.binary).decode("utf-8")
    assert "Код;Краткое наименование;Полное наименование;Группа;Единица измерения" in text
    assert nomenclature.name in text


def test_csv_report_range(range_item):
    """
    Проверка формирования отчета CSV для единицы измерения.
    """
    # Подготовка
    report = csv_report()

    # Действие
    result = report.build(range_item)

    # Проверка
    text = bytes(result.binary).decode("utf-8")
    assert "Код;Наименование;Коэффициент;Базовая единица" in text
    assert range_item.name in text


def test_xml_report_recipe(recipe):
    """
    Проверка формирования отчета XML для рецепта.
    """
    # Подготовка
    report = xml_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert isinstance(result, report_result_dto)
    assert len(result.text) > 0
    assert "<recipe>" in result.text
    assert f"<name>{recipe.name}</name>" in result.text
    for r in recipe.rows:
        assert f"<name>{r.nomenclature.name}</name>" in result.text


def test_xml_report_nomenclature(nomenclature):
    """
    Проверка формирования отчета XML для номенклатуры.
    """
    # Подготовка
    report = xml_report()

    # Действие
    result = report.build(nomenclature)

    # Проверка
    assert "<nomenclature>" in result.text
    assert f"<name>{nomenclature.name}</name>" in result.text
    assert f"<full_name>{nomenclature.full_name}</full_name>" in result.text


def test_xml_report_range(range_item):
    """
    Проверка формирования отчета XML для единицы измерения.
    """
    # Подготовка
    report = xml_report()

    # Действие
    result = report.build(range_item)

    # Проверка
    assert "<range>" in result.text
    assert f"<name>{range_item.name}</name>" in result.text


def test_html_report_recipe(recipe):
    """
    Проверка формирования отчета HTML для рецепта.
    """
    # Подготовка
    report = html_report()

    # Действие
    result = report.build(recipe)

    # Проверка
    assert "<!DOCTYPE html>" in result.text
    assert recipe.name in result.text
    for r in recipe.rows:
        assert r.nomenclature.name in result.text


def test_html_report_nomenclature(nomenclature):
    """
    Проверка формирования отчета HTML для номенклатуры.
    """
    # Подготовка
    report = html_report()

    # Действие
    result = report.build(nomenclature)

    # Проверка
    assert "<!DOCTYPE html>" in result.text
    assert nomenclature.name in result.text
    assert nomenclature.full_name in result.text


def test_html_report_range(range_item):
    """
    Проверка формирования отчета HTML для единицы измерения.
    """
    # Подготовка
    report = html_report()

    # Действие
    result = report.build(range_item)

    # Проверка
    assert "<!DOCTYPE html>" in result.text
    assert range_item.name in result.text
