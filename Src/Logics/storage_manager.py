from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
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
            self._recipes: dict[str, recipe_model] = {}
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

    @property
    def recipes(self) -> list[recipe_model]:
        """Список уникальных рецептов (технологических карт)."""
        return list(self._recipes.values())

    def add_range(self, item: range_model) -> None:
        """Добавить единицу измерения."""
        validator.validate(item, range_model)
        self._ranges[item.name.strip().lower()] = item

    def add_group(self, item: group_model) -> None:
        """Добавить группу."""
        validator.validate(item, group_model)
        self._groups[item.name.strip().lower()] = item

    def add_warehouse(self, item: warehouse_model) -> None:
        """Добавить склад."""
        validator.validate(item, warehouse_model)
        self._warehouses[item.name.strip().lower()] = item

    def add_nomenclature(self, item: nomenclature_model) -> None:
        """Добавить номенклатуру."""
        validator.validate(item, nomenclature_model)
        self._nomenclatures[item.name.strip().lower()] = item

    def add_recipe(self, item: recipe_model) -> None:
        """Добавить рецепт."""
        validator.validate(item, recipe_model)
        self._recipes[item.name.strip().lower()] = item

    def __generate_default_data(self) -> None:
        """
        Генерация первичных эталонных данных (первый старт) с использованием фабричных методов.
        Создаются базовые единицы измерения, группы, склады, номенклатура и рецепты
        (включая рецепты с полуфабрикатами и упаковкой).
        """
        self._ranges.clear()
        self._groups.clear()
        self._warehouses.clear()
        self._nomenclatures.clear()
        self._recipes.clear()

        # 1. Единицы измерения
        gramm = range_model.create_gramm()
        kg = range_model.create_kilogramm()
        ml = range_model.create_milliliter()
        liter = range_model.create_liter()
        piece = range_model.create_piece()

        for r in (gramm, kg, ml, liter, piece):
            self.add_range(r)

        # 2. Группы номенклатуры
        raw = group_model.create_raw()
        semi = group_model.create_semi()
        dishes = group_model.create_dishes()
        package = group_model.create_package()

        for g in (raw, semi, dishes, package):
            self.add_group(g)

        # 3. Склады
        main_wh = warehouse_model.create_main()
        kitchen_wh = warehouse_model.create_kitchen()
        delivery_wh = warehouse_model.create_delivery()

        for w in (main_wh, kitchen_wh, delivery_wh):
            self.add_warehouse(w)

        # 4. Номенклатура (сырье, полуфабрикаты, блюда, упаковка)
        flour = nomenclature_model.create_flour()
        sugar = nomenclature_model.create_sugar()
        butter = nomenclature_model.create_butter()
        egg = nomenclature_model.create_egg()
        vanilla = nomenclature_model.create_vanilla()
        condensed_milk = nomenclature_model.create_condensed_milk()

        shortcrust_dough = nomenclature_model.create_shortcrust_dough()
        cream = nomenclature_model.create_cream()
        waffle_cake = nomenclature_model.create_waffle_cake()
        cake_box = nomenclature_model.create_cake_box()

        for n in (
            flour, sugar, butter, egg, vanilla, condensed_milk,
            shortcrust_dough, cream, waffle_cake, cake_box
        ):
            self.add_nomenclature(n)

        # 5. Рецепты
        dough_recipe = recipe_model.create_dough_recipe()
        cream_recipe = recipe_model.create_cream_recipe()
        cake_recipe = recipe_model.create_waffle_cake_recipe()

        for r in (dough_recipe, cream_recipe, cake_recipe):
            self.add_recipe(r)


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
            "nomenclatures": self.nomenclatures,
            "recipes": self.recipes
        }

    def load(self, file_name: str = "") -> None:
        """
        Загрузка/инициализация хранилища (вызов convert).
        """
        self._is_loaded = self.convert()

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
