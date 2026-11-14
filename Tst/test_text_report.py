from Src.Logics.text_report import text_report
from Src.Models.recipe_model import recipe_model
from Src.Models.group_model import group_model


def test_success_text_report_all_recipe_rows_and_properties():
    """
    TXT содержит свойства рецепта и каждую строку его состава.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()

    # Действие
    result = text_report().build(recipe)

    # Проверка
    assert result.binary == []
    assert recipe.name in result.text
    assert recipe.steps in result.text
    assert "gross" in result.text and "net" in result.text
    for row in recipe.rows:
        assert row.id in result.text
        assert row.nomenclature.name in result.text


def test_success_text_report_simple_entity():
    """
    Справочник без коллекций обрабатывается тем же построителем.
    """
    # Подготовка
    group = group_model("Сырье")

    # Действие
    result = text_report().build(group)

    # Проверка
    assert f"id: {group.id}" in result.text
    assert "name: Сырье" in result.text
