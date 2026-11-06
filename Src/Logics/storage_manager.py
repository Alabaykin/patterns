import json
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception, operation_exception
from Src.Core.validator import validator
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Logics.settings_manager import settings_manager
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory


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
        Загрузка моделей из JSON-файла или инициализация хранилища при пустом имени файла.
        Данные заменяются только после успешного восстановления всех коллекций.
        """
        if not isinstance(file_name, str):
            raise arguments_exception("Имя файла должно быть строкой", "file_name")
        cleaned_file_name = file_name.strip()
        if not cleaned_file_name:
            self._is_loaded = self.convert()
            return

        try:
            with open(cleaned_file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise operation_exception(
                f"Не удалось загрузить JSON из файла '{cleaned_file_name}': {error}"
            ) from error

        collections = self._deserialize_collections(data)
        self._ranges = collections["ranges"]
        self._groups = collections["groups"]
        self._warehouses = collections["warehouses"]
        self._nomenclatures = collections["nomenclatures"]
        self._recipes = collections["recipes"]
        self._is_loaded = True

    def _deserialize_collections(self, data: dict) -> dict:
        """
        Восстановление коллекций во временные словари с проверкой структуры и уникальности.
        """
        model_types = {
            "ranges": range_model,
            "groups": group_model,
            "warehouses": warehouse_model,
            "nomenclatures": nomenclature_model,
            "recipes": recipe_model,
        }
        if not isinstance(data, dict):
            raise arguments_exception("Корень JSON хранилища должен быть словарем", "data")
        missing = model_types.keys() - data.keys()
        if missing:
            field = sorted(missing)[0]
            raise arguments_exception(f"Отсутствует коллекция '{field}'", field)
        unexpected = data.keys() - model_types.keys()
        if unexpected:
            field = str(next(iter(unexpected)))
            raise arguments_exception(f"Неизвестная коллекция '{field}'", field)

        factory = deserialize_factory()
        collections = {}
        for field, model_type in model_types.items():
            if not isinstance(data[field], list):
                raise arguments_exception(f"Коллекция '{field}' должна быть списком", field)
            deserializer = factory.create(model_type)
            items = {}
            identifiers = set()
            for item_data in data[field]:
                item = deserializer.deserialize(item_data)
                key = item.name.strip().lower()
                if key in items:
                    raise arguments_exception(f"Повторное наименование в коллекции '{field}'", field)
                if item.id in identifiers:
                    raise arguments_exception(f"Повторный идентификатор в коллекции '{field}'", field)
                items[key] = item
                identifiers.add(item.id)
            collections[field] = items
        return collections

    def save(self, file_name: str = "storage.json") -> str:
        """
        Выгрузка всех данных хранилища в один файл формата JSON.
        :param file_name: Путь к целевому файлу.
        :return: Имя сохраненного файла.
        """
        validator.validate(file_name, str)
        cleaned_file_name = file_name.strip()
        if not cleaned_file_name:
            cleaned_file_name = "storage.json"

        factory = convert_factory()
        payload = factory.serialize(self.data)
        with open(cleaned_file_name, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        return cleaned_file_name

    @property
    def is_loaded(self) -> bool:
        return self._is_loaded

    def get_by_type_and_id(self, entity_type: str, identifier: str):
        """
        Поиск сущности в хранилище по ее типу и идентификатору или наименованию.
        """
        if not isinstance(entity_type, str) or not isinstance(identifier, str):
            return None

        t = entity_type.strip().lower()
        items = []
        if t in ("номенклатура", "nomenclature", "nomenclature_model"):
            items = self.nomenclatures
        elif t in ("единица измерения", "единица_измерения", "единица", "range", "range_model", "unit"):
            items = self.ranges
        elif t in ("рецепт", "recipe", "recipe_model"):
            items = self.recipes
        elif t in ("группа", "group", "group_model"):
            items = self.groups
        elif t in ("склад", "warehouse", "warehouse_model"):
            items = self.warehouses
        else:
            return None

        clean_id = identifier.strip().lower()
        for item in items:
            if str(item.id).lower() == clean_id or str(item.name).lower() == clean_id:
                return item
        return None
