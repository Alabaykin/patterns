import pytest
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Core.exception import arguments_exception


@pytest.fixture
def sample_ingredients():
    raw_group = group_model.create_raw()
    kg = range_model.create_kilogramm()
    gramm = kg.base
    piece = range_model.create_piece()

    flour = nomenclature_model.create_flour()
    sugar = nomenclature_model.create_sugar()
    vanilla = nomenclature_model.create_vanilla()
    egg = nomenclature_model.create_egg()

    return {
        "kg": kg,
        "gramm": gramm,
        "piece": piece,
        "flour": flour,
        "sugar": sugar,
        "vanilla": vanilla,
        "egg": egg,
    }


def test_recipe_row_create_and_properties(sample_ingredients):
    """
    Проверка создания строки рецепта (recipe_row_model) и ее свойств.
    """
    flour = sample_ingredients["flour"]
    kg = sample_ingredients["kg"]

    row = recipe_row_model(flour, kg, gross=0.5, net=0.48)

    assert row.nomenclature == flour
    assert row.range == kg
    assert row.gross == 0.5
    assert row.net == 0.48
    assert row.name == flour.name
    assert row.id is not None


def test_recipe_row_factory_methods():
    """
    Проверка доменных фабричных методов recipe_row_model.
    """
    flour_row = recipe_row_model.create_flour_row(0.250, 0.250)
    assert flour_row.nomenclature.name == "Мука пшеничная"
    assert flour_row.gross == 0.250
    assert flour_row.net == 0.250

    dough_row = recipe_row_model.create_dough_row(0.550, 0.550)
    assert dough_row.nomenclature.name == "Песочное тесто"
    assert dough_row.gross == 0.550

    box_row = recipe_row_model.create_box_row(1.0, 1.0)
    assert box_row.nomenclature.name == "Коробка для торта"
    assert box_row.gross == 1.0


def test_recipe_row_validation(sample_ingredients):
    """
    Проверка валидации полей строки рецепта при некорректных данных.
    """
    flour = sample_ingredients["flour"]
    kg = sample_ingredients["kg"]

    # Отрицательный или нулевой брутто
    with pytest.raises(arguments_exception):
        recipe_row_model(flour, kg, gross=-1.0, net=1.0)

    with pytest.raises(arguments_exception):
        recipe_row_model(flour, kg, gross=0, net=1.0)

    # Некорректный тип нетто
    with pytest.raises(arguments_exception):
        recipe_row_model(flour, kg, gross=1.0, net="не число")


def test_recipe_create_and_initial_rows(sample_ingredients):
    """
    Проверка создания рецепта со списком строк.
    """
    flour = sample_ingredients["flour"]
    sugar = sample_ingredients["sugar"]
    kg = sample_ingredients["kg"]

    r1 = recipe_row_model(flour, kg, 0.5, 0.5)
    r2 = recipe_row_model(sugar, kg, 0.2, 0.2)

    recipe = recipe_model(
        name="Тесто",
        rows=[r1, r2],
        steps="Смешать ингредиенты",
        output_range=kg
    )

    assert recipe.name == "Тесто"
    assert len(recipe.rows) == 2
    assert recipe.steps == "Смешать ингредиенты"
    assert recipe.output_range == kg


def test_recipe_factory_methods():
    """
    Проверка создания рецептов через доменные фабричные методы.
    """
    dough_recipe = recipe_model.create_dough_recipe()
    assert dough_recipe.name == "Песочное тесто"
    assert len(dough_recipe.rows) == 5
    assert dough_recipe.target_nomenclature.name == "Песочное тесто"

    cream_recipe = recipe_model.create_cream_recipe()
    assert cream_recipe.name == "Крем со сгущенкой"
    assert len(cream_recipe.rows) == 2
    assert cream_recipe.target_nomenclature.name == "Крем со сгущенкой"

    cake_recipe = recipe_model.create_waffle_cake_recipe()
    assert cake_recipe.name == "Вафельный торт с кремом"
    assert len(cake_recipe.rows) == 3
    assert cake_recipe.target_nomenclature.name == "Вафельный торт"


def test_recipe_calculate_gross_and_net_without_conversion(sample_ingredients):
    """
    Проверка расчета Брутто и Нетто когда все ингредиенты в одной единице измерения.
    """
    flour = sample_ingredients["flour"]
    sugar = sample_ingredients["sugar"]
    kg = sample_ingredients["kg"]

    r1 = recipe_row_model(flour, kg, 0.500, 0.480)
    r2 = recipe_row_model(sugar, kg, 0.200, 0.190)

    recipe = recipe_model("Выпечка", [r1, r2], output_range=kg)

    assert recipe.calculate_gross() == 0.700
    assert recipe.calculate_net() == 0.670


def test_recipe_calculate_gross_and_net_with_conversion(sample_ingredients):
    """
    Проверка расчета Брутто и Нетто с конвертацией совместимых единиц (кг и грамм).
    """
    flour = sample_ingredients["flour"]
    vanilla = sample_ingredients["vanilla"]
    kg = sample_ingredients["kg"]
    gramm = sample_ingredients["gramm"]

    # Мука 0.5 кг, ванилин 50 грамм (= 0.05 кг)
    r1 = recipe_row_model(flour, kg, 0.500, 0.500)
    r2 = recipe_row_model(vanilla, gramm, 50.0, 50.0)

    recipe = recipe_model("Тесто с ванилином", [r1, r2], output_range=kg)

    # При расчете к кг: 0.5 кг + 0.05 кг = 0.55 кг
    assert recipe.calculate_gross(kg) == 0.55
    assert recipe.calculate_net(kg) == 0.55

    # При расчете к граммам: 500 г + 50 г = 550 г
    assert recipe.calculate_gross(gramm) == 550.0
    assert recipe.calculate_net(gramm) == 550.0


def test_recipe_add_row_recalculates_weight(sample_ingredients):
    """
    Проверка добавления нового ингредиента в рецепт и корректного пересчета веса.
    """
    flour = sample_ingredients["flour"]
    sugar = sample_ingredients["sugar"]
    kg = sample_ingredients["kg"]

    recipe = recipe_model("Рецепт динамический", output_range=kg)
    assert recipe.calculate_gross() == 0.0
    assert recipe.calculate_net() == 0.0

    # Добавляем муку
    recipe.add_row(recipe_row_model(flour, kg, 0.300, 0.280))
    assert recipe.calculate_gross() == 0.300
    assert recipe.calculate_net() == 0.280

    # Добавляем сахар
    recipe.add_row(recipe_row_model(sugar, kg, 0.150, 0.150))
    assert recipe.calculate_gross() == 0.450
    assert recipe.calculate_net() == 0.430


def test_recipe_remove_row_recalculates_weight(sample_ingredients):
    """
    Проверка исключения ингредиента из рецепта по имени или объекту строки и корректного пересчета.
    """
    flour = sample_ingredients["flour"]
    sugar = sample_ingredients["sugar"]
    kg = sample_ingredients["kg"]

    r1 = recipe_row_model(flour, kg, 0.300, 0.300)
    r2 = recipe_row_model(sugar, kg, 0.150, 0.150)

    recipe = recipe_model("Рецепт с удалением", [r1, r2], output_range=kg)
    assert recipe.calculate_gross() == 0.450

    # Исключаем сахар по имени номенклатуры
    removed = recipe.remove_row("Сахар")
    assert removed is True
    assert len(recipe.rows) == 1
    assert recipe.calculate_gross() == 0.300
    assert recipe.calculate_net() == 0.300

    # Исключаем муку по объекту строки
    removed_obj = recipe.remove_row(r1)
    assert removed_obj is True
    assert len(recipe.rows) == 0
    assert recipe.calculate_gross() == 0.0
    assert recipe.calculate_net() == 0.0
