import csv
from html import escape
from io import StringIO
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import pytest

from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.report_factory import report_factory
from Src.Logics.csv_report import csv_report
from Src.Logics.html_report import html_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.xml_report import xml_report
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.settings_model import settings_model


def test_success_report_every_format_and_entity():
    """
    Все пять построителей работают с простыми моделями и агрегатами.
    """
    for create_entity in [
        group_model.create_raw,
        warehouse_model.create_main,
        nomenclature_model.create_flour,
        range_model.create_kilogramm,
        recipe_model.create_dough_recipe,
    ]:
        for format_type in list(report_type_enum):
            # Подготовка
            entity = create_entity()
            report = report_factory(settings_model()).create(format_type)

            # Действие
            result = report.build(entity)
            content = bytes(result.binary).decode("utf-8") if report.is_attachment else result.text

            # Проверка
            assert entity.id in content
            assert entity.name in content
            assert bool(result.binary) == report.is_attachment
            assert bool(result.text) != report.is_attachment


def test_success_report_preserves_nested_recipe_content():
    """
    Каждый формат содержит собственные поля и все строки вложенного рецепта.
    """
    for format_type in list(report_type_enum):
        # Подготовка
        recipe = recipe_model.create_waffle_cake_recipe()
        child = recipe_model.create_dough_recipe()
        child.name = "Вложенный уникальный рецепт"
        child.steps = "Уникальная инструкция вложенного рецепта"
        recipe.rows[0].sub_recipe = child
        report = report_factory(settings_model()).create(format_type)

        # Действие
        result = report.build(recipe)
        content = bytes(result.binary).decode("utf-8") if report.is_attachment else result.text

        # Проверка
        assert child.name in content
        assert child.steps in content
        assert child.id in content
        for row in child.rows:
            assert row.id in content
            assert row.nomenclature.name in content


def test_success_csv_escaping_preserves_cells_and_all_rows():
    """
    Разделитель, кавычки и перевод строки в значении не меняют структуру CSV.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    special_name = 'Мука; "высший сорт"\nпросеянная'
    recipe.rows[0].nomenclature.name = special_name

    # Действие
    result = csv_report().build(recipe)
    rows = list(csv.DictReader(StringIO(bytes(result.binary).decode("utf-8")), delimiter=";"))

    # Проверка
    assert all(None not in row and all(value is not None for value in row.values()) for row in rows)
    ingredients = [row for row in rows if row["section"] == "rows" and row["field"] == "nomenclature"]
    assert len(ingredients) == len(recipe.rows)
    assert ingredients[0]["value"] == f"{special_name} ({recipe.rows[0].nomenclature.id})"
    assert {row["value"] for row in ingredients} == {
        f"{item.nomenclature.name} ({item.nomenclature.id})" for item in recipe.rows
    }


def test_success_xml_escaping_preserves_all_rows():
    """
    XML разбирается обратно без потери спецсимволов и строк состава.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    recipe.rows[-1].nomenclature.name = 'Ваниль <экстра> & "аромат"'

    # Действие
    root = ET.fromstring(xml_report().build(recipe).text)

    # Проверка
    rows = root.findall("./table[@name='rows']/row")
    assert len(rows) == len(recipe.rows)
    for node, source in zip(rows, recipe.rows):
        assert node.find("./cell[@name='nomenclature']").text == f"{source.nomenclature.name} ({source.nomenclature.id})"
        assert node.find("./cell[@name='gross']").text == str(source.gross)


def test_success_html_escapes_values_in_header_and_table():
    """
    И свойства модели, и ячейки таблиц содержат текст вместо исполняемой разметки.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    payload = '<script>alert("x")</script>'
    recipe.steps = payload
    recipe.rows[0].nomenclature.name = payload

    # Действие
    content = html_report().build(recipe).text

    # Проверка
    assert payload not in content
    assert escape(payload) in content
    assert content.count("<tbody>") >= 1
    assert content.count("<tr>") >= len(recipe.rows) + 1
    for row in recipe.rows:
        assert row.id in content


def test_success_markdown_escapes_markup_pipes_and_newlines():
    """
    Значения не создают новые колонки, строки таблицы или HTML-разметку.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    recipe.rows[0].nomenclature.name = "**Мука** | <b>сорт</b>\nновая строка"

    # Действие
    content = bytes(markdown_report().build(recipe).binary).decode("utf-8")

    # Проверка
    assert r"\*\*Мука\*\* \| &lt;b&gt;сорт&lt;/b&gt;<br>новая строка" in content
    assert "<b>" not in content
    assert sum(line.startswith("| ") for line in content.splitlines()) == len(recipe.rows) + 2


def test_success_report_new_model_and_new_property_without_registration():
    """
    Неизвестная фабрике модель и её свойства включаются автоматически.
    """
    for format_type in list(report_type_enum):
        # Подготовка
        model_type = type("delivery_model", (abstract_entity,), {"priority": property(lambda self: "urgent")})
        entity = model_type()
        entity.name = "Новая сущность"
        report = report_factory(settings_model()).create(format_type)

        # Действие
        result = report.build(entity)
        content = bytes(result.binary).decode("utf-8") if report.is_attachment else result.text

        # Проверка
        assert "priority" in content
        assert "urgent" in content
        assert entity.id in content


def test_raise_report_invalid_source():
    """
    Все форматы одинаково отклоняют источник, не являющийся моделью.
    """
    for format_type in list(report_type_enum):
        for source in [None, "recipe", {}]:
            # Подготовка
            report = report_factory(settings_model()).create(format_type)

            # Действие и проверка
            with pytest.raises(arguments_exception):
                report.build(source)


def test_success_report_response_content_type_and_download_name():
    """
    HTTP-ответ сохраняет формат, содержимое и корректное русское имя файла.
    """
    for format_type in list(report_type_enum):
        # Подготовка
        report = report_factory(settings_model()).create(format_type)
        result = report.build(group_model("Группа"))

        # Действие
        response = report.create_response(result, "отчёт тест")

        # Проверка
        assert response.mimetype == report.mimetype
        assert response.data == (bytes(result.binary) if report.is_attachment else result.text.encode("utf-8"))
        assert ("Content-Disposition" in response.headers) == report.is_attachment
        if report.is_attachment:
            disposition = response.headers["Content-Disposition"]
            disposition.encode("ascii")
            assert unquote(disposition.split("filename*=UTF-8''")[1]) == f"отчёт_тест.{report.file_extension}"
