import json
from threading import RLock
from types import MappingProxyType
from collections.abc import Mapping

from Src.Core.abstract_entity import abstract_entity
from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception, entity_conflict_exception, operation_exception
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.recipe_model import recipe_model
from Src.Logics.settings_manager import settings_manager
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.entity_types import entity_types, entity_links
from Src.Logics.reference_index import reference_index


class storage_manager(abstract_manager):
    """Кэш объектов с поиском по коду и имени; правила CRUD выполняются сервисом."""

    def __new__(cls):
        """Получить единственный экземпляр кэша."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        """Создать пустые коллекции, поисковые индексы и номер версии содержимого."""
        if not hasattr(self, "_initialized"):
            self.__records = {name: {} for name in entity_types}
            self.__by_id = {}
            self.__by_code = {}
            self.__revision = 0
            self.__is_loaded = False
            self.__lock = RLock()
            self._initialized = True

    @property
    def ranges(self) -> list[range_model]:
        """Список уникальных единиц измерения."""
        return self.items("ranges")

    @property
    def groups(self) -> list[group_model]:
        """Список уникальных групп номенклатуры."""
        return self.items("groups")

    @property
    def warehouses(self) -> list[warehouse_model]:
        """Список уникальных складов."""
        return self.items("warehouses")

    @property
    def nomenclatures(self) -> list[nomenclature_model]:
        """Список уникальных позиций номенклатуры."""
        return self.items("nomenclatures")

    @property
    def recipes(self) -> list[recipe_model]:
        """Список уникальных рецептов (технологических карт)."""
        return self.items("recipes")

    def _default_collections(self) -> dict:
        """
        Генерация первичных эталонных данных (первый старт) с использованием фабричных методов.
        Создаются базовые единицы измерения, группы, склады, номенклатура и рецепты
        (включая рецепты с полуфабрикатами и упаковкой).
        """
        creators = {
            "ranges": (
                range_model.create_gramm, range_model.create_kilogramm,
                range_model.create_milliliter, range_model.create_liter, range_model.create_piece,
            ),
            "groups": (group_model.create_raw, group_model.create_semi, group_model.create_dishes, group_model.create_package),
            "warehouses": (warehouse_model.create_main, warehouse_model.create_kitchen, warehouse_model.create_delivery),
            "nomenclatures": (
                nomenclature_model.create_flour, nomenclature_model.create_sugar,
                nomenclature_model.create_butter, nomenclature_model.create_egg,
                nomenclature_model.create_vanilla, nomenclature_model.create_condensed_milk,
                nomenclature_model.create_shortcrust_dough, nomenclature_model.create_cream,
                nomenclature_model.create_waffle_cake, nomenclature_model.create_cake_box,
            ),
            "recipes": (recipe_model.create_dough_recipe, recipe_model.create_cream_recipe, recipe_model.create_waffle_cake_recipe),
        }
        collections = {}
        for name, methods in creators.items():
            items = [method() for method in methods]
            collections[name] = {item.name.lower(): item for item in items}
        return self._link_collections(collections, match_names=True)

    def convert(self, settings=None) -> bool:
        """Установить данные первого старта."""
        with self.__lock:
            if settings is None:
                manager = settings_manager()
                if not manager.is_loaded:
                    manager.load()
                settings = manager.settings
            if settings.is_first:
                self._replace_all(self._default_collections())
            return True

    @property
    def data(self) -> dict:
        """Копии списков всех коллекций в формате файла хранилища."""
        with self.__lock:
            return {name: list(items.values()) for name, items in self.__records.items()}

    def load(self, file_name: str = "") -> None:
        """Заменить содержимое только после полной проверки загружаемых данных."""
        if not isinstance(file_name, str):
            raise arguments_exception("Имя файла должно быть строкой", "file_name")
        with self.__lock:
            if file_name.strip():
                self._replace_all(self._load_collections(file_name.strip()))
                self.__is_loaded = True
            else:
                self.__is_loaded = self.convert()

    def _deserialize_collections(self, data: dict) -> dict:
        """
        Восстановление коллекций в порядке файла с проверкой типа и уникальности моделей.
        """
        model_types = entity_types
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
        for field, records in data.items():
            if not isinstance(records, list):
                raise arguments_exception(f"Коллекция '{field}' должна быть списком", field)
            model_type = model_types[field]
            items = {}
            identifiers = set()
            for item_data in records:
                if not isinstance(item_data, dict):
                    raise arguments_exception("Данные модели должны быть словарём", "data")
                if "type" not in item_data:
                    raise arguments_exception(f"У модели в коллекции '{field}' отсутствует метка типа", "type")
                item = factory.deserialize(item_data)
                if not isinstance(item, model_type):
                    raise arguments_exception(f"Некорректный тип модели в коллекции '{field}'", field)
                key = item.name.strip().lower()
                if key in items:
                    raise arguments_exception(f"Повторное наименование в коллекции '{field}'", field)
                if item.id in identifiers:
                    raise arguments_exception(f"Повторный идентификатор в коллекции '{field}'", field)
                items[key] = item
                identifiers.add(item.id)
            collections[field] = items
        return self._link_collections(collections)

    def save(self, file_name: str = "storage.json") -> str:
        """Сохранить согласованный снимок коллекций общим сериализатором."""
        if not isinstance(file_name, str):
            raise arguments_exception("Имя файла должно быть строкой", "file_name")
        file_name = file_name.strip() or "storage.json"
        with self.__lock:
            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(convert_factory().serialize(self.data), file, ensure_ascii=False, indent=2)
        return file_name

    @property
    def is_loaded(self) -> bool:
        """Признак успешно загруженного содержимого."""
        return self.__is_loaded

    @property
    def lock(self):
        """Блокировка для атомарного выполнения сервисной операции над кэшем и индексом ссылок."""
        return self.__lock

    @property
    def revision(self) -> int:
        """Версия содержимого для обнаружения загрузки или записи другим сервисом."""
        return self.__revision

    @property
    def by_id(self) -> Mapping[str, abstract_entity]:
        """Представление индекса только для чтения, без копирования всего хранилища."""
        return MappingProxyType(self.__by_id)

    def _collection(self, name: str) -> dict:
        """Получить коллекцию по внутреннему ключу без разрешения внешних типов API."""
        if not isinstance(name, str) or name not in self.__records:
            raise arguments_exception("Неизвестная коллекция кэша", "collection")
        return self.__records[name]

    def items(self, collection: str) -> list[abstract_entity]:
        """Получить копию списка записей одной коллекции."""
        with self.__lock:
            return list(self._collection(collection).values())

    def find(self, identifier: str) -> abstract_entity | None:
        """Найти объект в индексе кодов за постоянное время."""
        with self.__lock:
            return self.__by_id.get(identifier)

    def code_owner(self, identifier: str) -> abstract_entity | None:
        """Найти владельца кода без учёта регистра для проверки уникальности."""
        with self.__lock:
            return self.__by_code.get(identifier.lower())

    def name_owner(self, collection: str, name: str) -> abstract_entity | None:
        """Найти запись по нормализованному имени в одной коллекции."""
        with self.__lock:
            return self._collection(collection).get(name.strip().lower())

    def _ensure_unique(self, collection: str, item: abstract_entity, exclude=None) -> None:
        """Защитить уникальные ключи кэша от перезаписи."""
        if not isinstance(item, abstract_entity):
            raise arguments_exception("Ожидается доменная модель", "item")
        owner = self.code_owner(item.id)
        if owner is not None and owner is not exclude:
            raise entity_conflict_exception(f"Код '{item.id}' уже занят")
        owner = self.name_owner(collection, item.name)
        if owner is not None and owner is not exclude:
            raise entity_conflict_exception(f"Наименование '{item.name}' уже занято")

    def insert(self, collection: str, item: abstract_entity) -> None:
        """Записать подготовленный объект и обновить поисковые индексы."""
        with self.__lock:
            self._ensure_unique(collection, item)
            self._collection(collection)[item.name.lower()] = item
            self.__by_id[item.id] = item
            self.__by_code[item.id.lower()] = item
            self.__revision += 1

    def replace(self, collection: str, target: abstract_entity, candidate: abstract_entity) -> None:
        """Применить проверенное состояние с сохранением экземпляра и перестройкой его ключей."""
        with self.__lock:
            self._ensure_unique(collection, candidate, target)
            records = self._collection(collection)
            if records.get(target.name.lower()) is not target or type(target) is not type(candidate):
                raise arguments_exception("Обновляемый объект не соответствует записи кэша", "target")
            old_id, old_name = target.id, target.name.lower()
            del records[old_name]
            del self.__by_id[old_id]
            del self.__by_code[old_id.lower()]
            target.replace_state(candidate)
            records[target.name.lower()] = target
            self.__by_id[target.id] = target
            self.__by_code[target.id.lower()] = target
            self.__revision += 1

    def remove(self, collection: str, item: abstract_entity) -> None:
        """Удалить проверенную сервисом запись и её поисковые ключи."""
        with self.__lock:
            records = self._collection(collection)
            if records.get(item.name.lower()) is not item:
                raise arguments_exception("Удаляемый объект отсутствует в коллекции", "item")
            del records[item.name.lower()]
            del self.__by_id[item.id]
            del self.__by_code[item.id.lower()]
            self.__revision += 1

    def _replace_all(self, collections: dict) -> None:
        """Подготовить новые поисковые индексы до атомарной замены всех коллекций."""
        by_id, by_code = {}, {}
        for items in collections.values():
            for item in items.values():
                if item.id.lower() in by_code:
                    raise arguments_exception(f"Повторный идентификатор '{item.id}'", "id")
                by_id[item.id] = item
                by_code[item.id.lower()] = item
        self.__records = collections
        self.__by_id, self.__by_code = by_id, by_code
        self.__revision += 1

    def clear(self) -> None:
        """Очистить все коллекции с обновлением версии и поисковых индексов."""
        with self.__lock:
            self._replace_all({name: {} for name in self.__records})
            self.__is_loaded = False

    def _load_collections(self, file_name: str) -> dict:
        """Прочитать и полностью проверить файл до изменения кэша."""
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise operation_exception(f"Не удалось загрузить JSON из файла '{file_name}': {error}") from error
        return self._deserialize_collections(data)

    def _link_collections(self, collections: dict, match_names: bool = False) -> dict:
        """Связать временные коллекции общими экземплярами, не затрагивая текущее хранилище."""
        roots = [item for items in collections.values() for item in items.values()]
        by_id = {item.id: item for item in roots}
        if len(by_id) != len(roots):
            raise arguments_exception("Повторный идентификатор сущности", "id")
        by_name = {(type(item), item.name.lower()): item for item in roots}
        serializer = convert_factory()
        links = []
        for item in roots:
            for owner, field in entity_links(item):
                value = getattr(owner, field)
                if value is None:
                    continue
                target = by_name.get((type(value), value.name.lower())) if match_names else by_id.get(value.id)
                if target is None or type(target) is not type(value):
                    raise arguments_exception(f"Ссылка на отсутствующую сущность '{value.name}' ({value.id})", field)
                if not match_names and serializer.serialize(value) != serializer.serialize(target):
                    raise arguments_exception(f"Противоречивые данные ссылки '{value.id}'", field)
                links.append((owner, field, target))
        for owner, field, target in links:
            setattr(owner, field, target)
        reference_index().rebuild(by_id)
        return collections
