from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Logics.settings_manager import settings_manager


class storage_manager(abstract_manager):
    """
    Менеджер хранилища справочников (Singleton).
    Хранит уникальные объекты единиц измерения, групп номенклатуры, складов и номенклатуры в оперативной памяти (кэш).
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(storage_manager, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._ranges: dict[str, range_model] = {}
            self._groups: dict[str, group_model] = {}
            self._warehouses: dict[str, warehouse_model] = {}
            self._nomenclatures: dict[str, nomenclature_model] = {}
            self._is_loaded = False
            self._initialized = True

    @property
    def ranges(self) -> list[range_model]:
        """Список уникальных единиц измерения."""
        return list(self._ranges.values())

    @property
    def groups(self) -> list[group_model]:
        """Список уникальных групп номенклатуры."""
        return list(self._groups.values())

    @property
    def warehouses(self) -> list[warehouse_model]:
        """Список уникальных складов."""
        return list(self._warehouses.values())

    @property
    def nomenclatures(self) -> list[nomenclature_model]:
        """Список уникальных позиций номенклатуры."""
        return list(self._nomenclatures.values())

    def add_range(self, item: range_model) -> None:
        """Добавить единицу измерения с обеспечением уникальности."""
        validator.validate(item, range_model)
        self._ranges[item.name.strip().lower()] = item

    def add_group(self, item: group_model) -> None:
        """Добавить группу с обеспечением уникальности."""
        validator.validate(item, group_model)
        self._groups[item.name.strip().lower()] = item

    def add_warehouse(self, item: warehouse_model) -> None:
        """Добавить склад с обеспечением уникальности."""
        validator.validate(item, warehouse_model)
        self._warehouses[item.name.strip().lower()] = item

    def add_nomenclature(self, item: nomenclature_model) -> None:
        """Добавить номенклатуру с обеспечением уникальности."""
        validator.validate(item, nomenclature_model)
        self._nomenclatures[item.name.strip().lower()] = item

    def __generate_default_data(self) -> None:
        """
        Генерация первичных эталонных данных (первый старт).
        Создаются базовые единицы измерения, группы, склады и номенклатура для рецептов.
        """
        self._ranges.clear()
        self._groups.clear()
        self._warehouses.clear()
        self._nomenclatures.clear()

        # 1. Единицы измерения
        gramm = range_model("грамм", 1.0)
        kg = range_model("кг", 1000.0, gramm)
        ml = range_model("мл", 1.0)
        liter = range_model("л", 1000.0, ml)
        piece = range_model("шт", 1.0)

        for r in (gramm, kg, ml, liter, piece):
            self.add_range(r)

        # 2. Группы номенклатуры
        raw = group_model("Сырье")
        semi = group_model("Полуфабрикаты")
        dishes = group_model("Блюда")
        package = group_model("Упаковка")

        for g in (raw, semi, dishes, package):
            self.add_group(g)

        # 3. Склады
        main_wh = warehouse_model("Основной склад")
        kitchen_wh = warehouse_model("Кухня")
        delivery_wh = warehouse_model("Зона доставки")

        for w in (main_wh, kitchen_wh, delivery_wh):
            self.add_warehouse(w)

        # 4. Номенклатура (сырье, полуфабрикат, блюдо)
        flour = nomenclature_model("Мука пшеничная", "Мука пшеничная высший сорт", raw, kg)
        sugar = nomenclature_model("Сахар", "Сахар-песок белый", raw, kg)
        butter = nomenclature_model("Сливочное масло", "Масло сливочное 82.5%", raw, kg)
        egg = nomenclature_model("Яйцо куриное", "Яйцо куриное категории С0", raw, piece)
        vanilla = nomenclature_model("Ванилин", "Ванилин кристаллический", raw, gramm)

        shortcrust_dough = nomenclature_model("Песочное тесто", "Тесто песочное полуфабрикат", semi, kg)
        waffle_cake = nomenclature_model("Вафельный торт", "Торт песочно-вафельный с кремом", dishes, piece)

        for n in (flour, sugar, butter, egg, vanilla, shortcrust_dough, waffle_cake):
            self.add_nomenclature(n)

    def convert(self, settings=None) -> bool:
        """
        Обработка данных при первом старте.
        Если is_first == True, формируются эталонные первичные данные в оперативной памяти (кэш).
        Параметр settings позволяет передать кастомные настройки (например, в тестах).
        """
        if settings is None:
            sm = settings_manager()
            if not sm.is_loaded:
                sm.load()
            settings = sm.settings

        is_first = True
        if settings is not None:
            is_first = settings.is_first

        if is_first:
            self.__generate_default_data()

        return True

    @property
    def data(self) -> dict:
        """
        Агрегированный словарь всех коллекций хранилища.
        """
        return {
            "ranges": self.ranges,
            "groups": self.groups,
            "warehouses": self.warehouses,
            "nomenclatures": self.nomenclatures
        }

    def load(self, file_name: str = "") -> None:
        """
        Загрузка/инициализация хранилища (вызов convert).
        """
        self._is_loaded = self.convert()

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded


