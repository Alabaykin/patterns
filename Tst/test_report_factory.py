import pytest
from Src.Logics.report_factory import report_factory
from Src.Logics.text_report import text_report
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Dtos.report_result_dto import report_result_dto
from Src.Models.recipe_model import recipe_model
from Src.Core.exception import arguments_exception


def test_report_factory_create_valid_type():
    """
    Проверка создания отчёта при передаче корректного типа отчёта.
    """
    # Подготовка
    factory = report_factory()

    # Действие
    report = factory.create(report_type_enum.TXT)

    # Проверка
    assert report is not None
    assert isinstance(report, text_report)
    assert isinstance(report, abstract_report)


def test_report_factory_create_invalid_type_raises_exception():
    """
    Проверка обработки некорректного типа отчёта.
    """
    # Подготовка
    factory = report_factory()
    # Проверка
    with pytest.raises(arguments_exception):
        factory.create(999)


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
