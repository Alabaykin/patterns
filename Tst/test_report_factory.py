import pytest
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Logics.markdown_report import markdown_report
from Src.Logics.csv_report import csv_report
from Src.Logics.xml_report import xml_report
from Src.Logics.html_report import html_report
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Models.settings_model import settings_model
from Src.Core.exception import arguments_exception


def test_report_factory_create_valid_type():
    """
    Проверка создания отчёта при передаче корректного типа отчёта.
    """
    # Подготовка
    factory = report_factory()

    # Действие
    report = factory.create(report_type_enum.TXT)
    md_report = factory.create(report_type_enum.MARKDOWN)
    c_report = factory.create(report_type_enum.CSV)
    x_report = factory.create(report_type_enum.XML)
    h_report = factory.create(report_type_enum.HTML)

    # Проверка
    assert report is not None
    assert isinstance(report, text_report)
    assert isinstance(report, abstract_report)
    assert isinstance(md_report, markdown_report)
    assert isinstance(c_report, csv_report)
    assert isinstance(x_report, xml_report)
    assert isinstance(h_report, html_report)


def test_report_factory_create_invalid_type_raises_exception():
    """
    Проверка обработки некорректного типа отчёта.
    """
    # Подготовка
    factory = report_factory()

    # Действие и проверка
    with pytest.raises(arguments_exception):
        factory.create(999)


def test_report_factory_create_default_from_settings():
    """
    Проверка создания отчета по умолчанию из инкапсулированных настроек.
    """
    # Подготовка
    settings = settings_model()
    settings.response_format = report_type_enum.XML
    factory = report_factory(settings)

    # Действие
    rep = factory.create_default()

    # Проверка
    assert isinstance(rep, xml_report)

    # Действие
    settings.format = report_type_enum.MARKDOWN
    rep_md = factory.create_default()

    # Проверка
    assert isinstance(rep_md, markdown_report)


def test_report_factory_integration_build_report():
    """
    Созданный через фабрику отчёт корректно выполняет
    свою бизнес-логику.
    """
    # Подготовка
    factory = report_factory()
    recipe = recipe_model.create_dough_recipe()

    # Действие
    report = factory.create(report_type_enum.TXT)
    result = report.build(recipe)

    # Проверка
    assert result is not None
    assert isinstance(result, report_result_dto)
    assert isinstance(result.text, str)
    assert len(result.text) > 0
    assert "Код | Наименование | Брутто | Нетто" in result.text
    for row in recipe.rows:
        assert row.nomenclature.name in result.text


def test_report_factory_create_specialized_reports():
    """
    Проверка создания специализированных генераторов отчетов по паре (формат, сущность).
    """
    # Подготовка
    from Src.Logics.csv_report import recipe_csv_report
    from Src.Logics.markdown_report import nomenclature_markdown_report
    from Src.Logics.xml_report import range_xml_report
    factory = report_factory()

    # Действие: по строковому имени
    rep_csv = factory.create(report_type_enum.CSV, "recipe")
    rep_md = factory.create(report_type_enum.MARKDOWN, "nomenclature")
    rep_xml = factory.create(report_type_enum.XML, "range")

    # Проверка
    assert isinstance(rep_csv, recipe_csv_report)
    assert isinstance(rep_md, nomenclature_markdown_report)
    assert isinstance(rep_xml, range_xml_report)


def test_report_factory_create_by_entity_type_and_instance():
    """
    Проверка создания отчета через фабрику передавая тип сущности или экземпляр модели.
    """
    factory = report_factory()
    recipe = recipe_model.create_dough_recipe()

    from Src.Logics.Reports.Html.recipe_html_report import recipe_html_report
    from Src.Logics.Reports.Csv.recipe_csv_report import recipe_csv_report

    # Передача класса модели
    rep_by_type = factory.create(report_type_enum.HTML, recipe_model)
    assert isinstance(rep_by_type, recipe_html_report)

    # Передача экземпляра модели
    rep_by_instance = factory.create(report_type_enum.CSV, recipe)
    assert isinstance(rep_by_instance, recipe_csv_report)


def test_report_factory_create_default_with_entity():
    """
    Проверка create_default с передачей сущности.
    """
    settings = settings_model()
    settings.response_format = report_type_enum.HTML
    factory = report_factory(settings)

    from Src.Logics.Reports.Html.recipe_html_report import recipe_html_report
    rep = factory.create_default("recipe")
    assert isinstance(rep, recipe_html_report)


def test_report_factory_invalid_entity_raises():
    """
    Проверка вызова с неизвестной сущностью.
    """
    factory = report_factory()
    with pytest.raises(arguments_exception):
        factory.create(report_type_enum.CSV, "unknown_entity_123")

