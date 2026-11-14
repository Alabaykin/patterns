from unittest.mock import patch

from Src.Core.abstract_entity import abstract_entity
from Src.Logics.report_data_builder import report_data_builder
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model


def test_success_report_data_all_recipe_rows():
    """
    Все строки сохраняют идентификаторы, ссылки и веса, включая последнюю строку.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()

    # Действие
    data = report_data_builder().build(recipe)

    # Проверка
    table = next(table for table in data.tables if table.name == "rows")
    assert len(table.rows) == len(recipe.rows)
    for values, source in zip(table.rows, recipe.rows):
        record = dict(zip(table.columns, values))
        assert record["id"] == source.id
        assert record["nomenclature"] == f"{source.nomenclature.name} ({source.nomenclature.id})"
        assert record["gross"] == str(source.gross)
        assert record["net"] == str(source.net)


def test_success_report_data_nested_recipes_at_multiple_levels():
    """
    Вложенные агрегаты раскрываются глубже одного уровня с сохранением собственных полей.
    """
    # Подготовка
    root = recipe_model.create_waffle_cake_recipe()
    child = recipe_model.create_dough_recipe()
    grandchild = recipe_model.create_cream_recipe()
    root.rows[0].sub_recipe = child
    child.rows[-1].sub_recipe = grandchild

    # Действие
    data = report_data_builder().build(root)

    # Проверка
    tables = {table.name: table for table in data.tables}
    assert len(tables["rows[0].sub_recipe.rows"].rows) == len(child.rows)
    assert len(tables["rows[0].sub_recipe.rows[4].sub_recipe.rows"].rows) == len(grandchild.rows)
    child_header = tables["rows[0].sub_recipe"]
    assert dict(zip(child_header.columns, child_header.rows[0]))["steps"] == child.steps


def test_success_report_data_all_collections_and_heterogeneous_rows():
    """
    Несколько списков, словарь и неодинаковые строки обрабатываются без потери колонок.
    """
    # Подготовка
    group = group_model("Группа")
    unit = range_model.create_kilogramm()
    model_type = type("batch_model", (abstract_entity,), {
        "items": property(lambda self: [group, unit]),
        "notes": property(lambda self: ["Первая", "Последняя"]),
        "options": property(lambda self: {"color": "red", "count": 2}),
        "empty": property(lambda self: []),
    })
    source = model_type()
    source.name = "Партия"

    # Действие
    tables = {table.name: table for table in report_data_builder().build(source).tables}

    # Проверка
    assert set(tables) == {"items", "notes", "options", "empty"}
    assert len(tables["items"].rows) == 2
    coefficient = tables["items"].columns.index("coefficient")
    assert [row[coefficient] for row in tables["items"].rows] == ["", "1000.0"]
    assert tables["notes"].rows == [["Первая"], ["Последняя"]]
    assert tables["options"].columns == ["key", "value"]
    assert tables["options"].rows == [["color", "red"], ["count", "2"]]
    assert tables["empty"].rows == []


def test_success_report_data_self_reference_and_cycle_are_finite():
    """
    Циклическая ссылка остаётся значением ссылки и не вызывает бесконечную рекурсию.
    """
    # Подготовка
    recipe = recipe_model.create_dough_recipe()
    recipe.rows[0].sub_recipe = recipe

    # Действие
    data = report_data_builder().build(recipe)

    # Проверка
    assert len(data.tables) == 1
    table = data.tables[0]
    assert table.rows[0][table.columns.index("sub_recipe")] == f"{recipe.name} ({recipe.id})"


def test_success_report_data_shared_reference_is_expanded_for_each_path():
    """
    Общий вложенный рецепт отображается в обеих строках, а не исчезает из второй.
    """
    # Подготовка
    recipe = recipe_model.create_waffle_cake_recipe()
    nested = recipe_model.create_dough_recipe()
    recipe.rows[0].sub_recipe = nested
    recipe.rows[1].sub_recipe = nested

    # Действие
    tables = {table.name: table for table in report_data_builder().build(recipe).tables}

    # Проверка
    assert len(tables["rows[0].sub_recipe.rows"].rows) == len(nested.rows)
    assert len(tables["rows[1].sub_recipe.rows"].rows) == len(nested.rows)


def test_success_report_data_reads_new_public_property():
    """
    Новое свойство существующей модели появляется без изменения построителя.
    """
    # Подготовка
    group = group_model("Сырье")

    # Действие
    with patch.object(group_model, "description", property(lambda self: "Новое поле"), create=True):
        fields = {field.name: field.value for field in report_data_builder().build(group).fields}

    # Проверка
    assert fields["description"] == "Новое поле"
    assert fields["name"] == "Сырье"
    assert "type" not in fields
