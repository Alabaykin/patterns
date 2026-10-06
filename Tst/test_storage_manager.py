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
    assert "грамм" in range_names
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
    duplicate = range_model("грамм", 1.0)
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
    Проверка свойства data: содержит все 4 категории справочников.
    """
    sm = storage_manager()
    sm.load()

    data = sm.data
    assert isinstance(data, dict)
    assert "ranges" in data
    assert "groups" in data
    assert "warehouses" in data
    assert "nomenclatures" in data
    assert len(data["ranges"]) > 0


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

    sm.convert(settings=custom_settings)

    assert len(sm.ranges) == 0
    assert len(sm.groups) == 0
    assert len(sm.warehouses) == 0
    assert len(sm.nomenclatures) == 0

    # Восстанавливаем данные для последующих тестов
    sm.convert()


