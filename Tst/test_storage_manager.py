import pytest
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception



def test_storage_manager_singleton():
    """
    Проверка работы шаблона Singleton для storage_manager:
    два вызова возвращают один и тот же экземпляр.
    """
    # Подготовка и действие
    sm1 = storage_manager()
    sm2 = storage_manager()

    # Проверка
    assert sm1 is sm2
    assert str(sm1) == str(sm2)


def test_storage_manager_first_start_generate_data():
    """
    Проверка генерации первичных эталонных данных при первом старте:
    должны быть созданы единицы измерения, группы, склады и номенклатура.
    """
    # Подготовка
    sm = storage_manager()

    # Действие
    sm.load()

    # Проверка
    assert sm.is_loaded is True
    assert len(sm.ranges) > 0
    assert len(sm.groups) > 0
    assert len(sm.warehouses) > 0
    assert len(sm.nomenclatures) > 0

    # Проверка наличия ключевых элементов
    range_names = [r.name for r in sm.ranges]
    assert "гр" in range_names
    assert "кг" in range_names
    assert "шт" in range_names

    group_names = [g.name for g in sm.groups]
    assert "Сырье" in group_names
    assert "Блюда" in group_names

    warehouse_names = [w.name for w in sm.warehouses]
    assert "Основной склад" in warehouse_names
    assert "Кухня" in warehouse_names

    nomenclature_names = [n.name for n in sm.nomenclatures]
    assert "Мука пшеничная" in nomenclature_names
    assert "Сливочное масло" in nomenclature_names
    assert "Вафельный торт" in nomenclature_names


def test_storage_manager_unique_ranges():
    """
    Проверка обеспечения уникальности элементов в коллекции единиц измерения.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.ranges)

    # Добавляем дубликат с тем же именем
    duplicate = range_model("гр", 1.0)
    sm.add_range(duplicate)

    # Количество не должно вырасти
    assert len(sm.ranges) == initial_count


def test_storage_manager_unique_warehouses():
    """
    Проверка обеспечения уникальности складов.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.warehouses)

    # Добавляем склад с существующим именем
    duplicate = warehouse_model("Кухня")
    sm.add_warehouse(duplicate)

    assert len(sm.warehouses) == initial_count


def test_storage_manager_unique_nomenclatures():
    """
    Проверка обеспечения уникальности номенклатуры.
    """
    sm = storage_manager()
    sm.load()
    initial_count = len(sm.nomenclatures)

    # Добавляем номенклатуру с существующим именем
    raw_group = sm.groups[0]
    kg_range = sm.ranges[0]
    duplicate = nomenclature_model("Мука пшеничная", "Мука пшеничная сорт 1", raw_group, kg_range)
    sm.add_nomenclature(duplicate)

    assert len(sm.nomenclatures) == initial_count


def test_storage_manager_validation_type():
    """
    Проверка валидации типов при добавлении в хранилище.
    """
    sm = storage_manager()

    with pytest.raises(arguments_exception):
        sm.add_range("не валидный объект")

    with pytest.raises(arguments_exception):
        sm.add_warehouse(12345)



def test_storage_manager_data_property():
    """
    Проверка свойства data: содержит все 5 категорий справочников.
    """
    sm = storage_manager()
    sm.load()

    data = sm.data
    assert isinstance(data, dict)
    assert "ranges" in data
    assert "groups" in data
    assert "warehouses" in data
    assert "nomenclatures" in data
    assert "recipes" in data
    assert len(data["ranges"]) > 0
    assert len(data["recipes"]) > 0


def test_storage_manager_convert_with_custom_settings_is_first_false():
    """
    Проверка конвертации при is_first == False: первичные данные не создаются.
    """
    from Src.Models.settings_model import settings_model

    custom_settings = settings_model()
    custom_settings.is_first = False

    sm = storage_manager()
    # Очищаем перед тестом
    sm._ranges.clear()
    sm._groups.clear()
    sm._warehouses.clear()
    sm._nomenclatures.clear()
    sm._recipes.clear()

    sm.convert(settings=custom_settings)

    assert len(sm.ranges) == 0
    assert len(sm.groups) == 0
    assert len(sm.warehouses) == 0
    assert len(sm.nomenclatures) == 0
    assert len(sm.recipes) == 0

    # Восстанавливаем данные для последующих тестов
    sm.convert()


def test_storage_manager_recipes_first_start_present():
    """
    Проверка наличия сгенерированных рецептов при первом старте:
    полуфабрикаты ('Песочное тесто', 'Крем со сгущенкой') и блюдо с упаковкой ('Вафельный торт с кремом').
    """
    sm = storage_manager()
    sm.load()

    recipe_names = [r.name for r in sm.recipes]
    assert "Песочное тесто" in recipe_names
    assert "Крем со сгущенкой" in recipe_names
    assert "Вафельный торт с кремом" in recipe_names

    # Проверяем рецепт торта
    cake_recipe = next(r for r in sm.recipes if r.name == "Вафельный торт с кремом")
    row_nomenclatures = [row.nomenclature.name for row in cake_recipe.rows]
    assert "Песочное тесто" in row_nomenclatures  # полуфабрикат
    assert "Крем со сгущенкой" in row_nomenclatures  # полуфабрикат
    assert "Коробка для торта" in row_nomenclatures  # упаковка

    # Проверка веса Брутто и Нетто (0.550 + 0.300 + 1.0 шт = 1.85)
    assert cake_recipe.calculate_gross() == 1.85
    assert cake_recipe.calculate_net() == 1.85


def test_storage_manager_recipe_ingredients_weight_calculations():
    """
    Проверка расчета веса Брутто и Нетто для рецепта песочного теста:
    мука 0.250 кг + масло 0.100 кг + сахар 0.150 кг + 2 шт яйца + ванилин 0.002 кг = 2.502 (в кг).
    """
    sm = storage_manager()
    sm.load()

    kg = next(r for r in sm.ranges if r.name == "кг")
    dough_recipe = next(r for r in sm.recipes if r.name == "Песочное тесто")

    gross = dough_recipe.calculate_gross(kg)
    net = dough_recipe.calculate_net(kg)

    # 0.25 + 0.10 + 0.15 + 2.0 (шт) + 0.002 (ванилин 2г = 0.002 кг) = 2.502
    assert gross == 2.502
    assert net == 2.502



