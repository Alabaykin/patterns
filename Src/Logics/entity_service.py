from uuid import uuid4

from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception, entity_conflict_exception, entity_not_found_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Logics.entity_types import entity_types
from Src.Logics.reference_index import reference_index
from Src.Logics.storage_manager import storage_manager


class entity_service:
    """Сервис CRUD: разрешение типов, десериализация, доменные проверки и учёт связей."""

    def __new__(cls, storage: storage_manager):
        """Получить единственный экземпляр сервиса."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, storage: storage_manager):
        """Сохранить хранилище и построить индекс связей между сущностями."""
        if not isinstance(storage, storage_manager):
            raise arguments_exception("Ожидается хранилище сущностей", "storage")
        if hasattr(self, "_initialized"):
            return
        self.__storage = storage
        self.__references = reference_index()
        self.__revision = -1
        with self.__storage.lock:
            self._sync_references()
        self._initialized = True

    @property
    def entity_types(self) -> list[str]:
        """Ключи зарегистрированных типов API."""
        return [model.__name__ for model in entity_types.values()]

    @staticmethod
    def _resolve(entity_type: str) -> tuple[str, type]:
        """Найти коллекцию и модель по названию типа."""
        if not isinstance(entity_type, str):
            raise arguments_exception("Тип сущности должен быть строкой", "entity_type")
        key = entity_type.strip().lower()
        for collection, model in entity_types.items():
            if key in (collection, model.__name__, model.__name__.removesuffix("_model")):
                return collection, model
        raise entity_not_found_exception(f"Неизвестный тип сущности '{entity_type}'")

    def _sync_references(self) -> None:
        """Перестроить индекс после загрузки или изменения кэша вне сервиса."""
        if self.__revision != self.__storage.revision:
            index = reference_index()
            index.rebuild(self.__storage.by_id)
            self.__references = index
            self.__revision = self.__storage.revision

    def list_entities(self, entity_type: str) -> list[abstract_entity]:
        """Получить записи выбранного типа."""
        collection, _ = self._resolve(entity_type)
        return self.__storage.items(collection)

    def get(self, entity_type: str, identifier: str) -> abstract_entity:
        """Получить сущность строго по коду и проверить принадлежность выбранному типу."""
        _, model = self._resolve(entity_type)
        if not isinstance(identifier, str) or not identifier.strip():
            raise arguments_exception("Код должен быть непустой строкой", "id")
        with self.__storage.lock:
            item = self.__storage.find(identifier.strip())
            if item is None or type(item) is not model:
                raise entity_not_found_exception(f"Не найдена сущность '{entity_type}' с кодом '{identifier}'")
            return item

    def get_by_type_and_id(self, entity_type: str, identifier: str):
        """Сохранить поиск по коду или имени для прежних методов отчётов."""
        if not isinstance(entity_type, str) or not isinstance(identifier, str):
            return None
        try:
            collection, model = self._resolve(entity_type)
        except entity_not_found_exception:
            return None
        with self.__storage.lock:
            item = self.__storage.code_owner(identifier.strip())
            if item is not None and type(item) is model:
                return item
            return self.__storage.name_owner(collection, identifier)

    def find_referrers(self, target: abstract_entity) -> list[abstract_entity]:
        """Найти прямых и транзитивных пользователей по индексированным рёбрам."""
        if not isinstance(target, abstract_entity):
            raise arguments_exception("Ожидается доменная модель", "target")
        with self.__storage.lock:
            self._sync_references()
            return [self.__storage.find(identifier) for identifier in self.__references.referrers(target.id)]

    def _ensure_not_referenced(self, target: abstract_entity) -> None:
        """Запретить удаление или смену кода при наличии входящих ссылок."""
        references = self.find_referrers(target)
        if references:
            descriptions = ", ".join(f"{item.name} ({item.id})" for item in references)
            raise entity_conflict_exception(f"Сущность '{target.name}' ({target.id}) используется: {descriptions}")

    def _build(self, model: type, data: dict, existing=None) -> abstract_entity:
        """Собрать кандидата общим механизмом десериализации с доступом к индексу кэша."""
        if not isinstance(data, dict):
            raise arguments_exception("Тело запроса должно быть JSON-объектом", "data")
        expected_type = f"{model.__module__}.{model.__qualname__}"
        if data.get("type", expected_type) != expected_type:
            raise arguments_exception("Тип JSON не соответствует типу сущности в адресе", "type")
        payload = {**data, "type": expected_type}
        payload.setdefault("id", existing.id if existing is not None else str(uuid4()))
        return deserialize_factory(self.__storage.by_id).create(expected_type).deserialize(payload)

    def _prepare(self, collection: str, candidate: abstract_entity, existing=None) -> set[str]:
        """Проверить ключи и новые рёбра до изменения объектов или индекса ссылок."""
        owner = self.__storage.code_owner(candidate.id)
        if owner is not None and owner is not existing:
            raise entity_conflict_exception(f"Код '{candidate.id}' уже занят")
        owner = self.__storage.name_owner(collection, candidate.name)
        if owner is not None and owner is not existing:
            raise entity_conflict_exception(f"Наименование '{candidate.name}' уже занято")
        if existing is not None and existing.id != candidate.id:
            self._ensure_not_referenced(existing)
        return self.__references.prepare(candidate, self.__storage.by_id, existing)

    def create(self, entity_type: str, data: dict) -> abstract_entity:
        """Создать проверенную сущность и добавить только её рёбра в индекс."""
        collection, model = self._resolve(entity_type)
        with self.__storage.lock:
            self._sync_references()
            candidate = self._build(model, data)
            targets = self._prepare(collection, candidate)
            self.__storage.insert(collection, candidate)
            self.__references.update(candidate.id, targets)
            self.__revision = self.__storage.revision
            return candidate

    def add(self, item: abstract_entity) -> None:
        """Добавить готовую модель через ту же десериализацию и проверки, сохранив её экземпляр."""
        if type(item) not in entity_types.values():
            raise arguments_exception("Неподдерживаемый тип модели", "item")
        collection, model = self._resolve(type(item).__name__)
        with self.__storage.lock:
            self._sync_references()
            candidate = self._build(model, convert_factory().serialize(item))
            targets = self._prepare(collection, candidate)
            item.replace_state(candidate)
            self.__storage.insert(collection, item)
            self.__references.update(item.id, targets)
            self.__revision = self.__storage.revision

    def update(self, entity_type: str, identifier: str, data: dict) -> abstract_entity:
        """Обновить состояние на месте и заменить только исходящие рёбра изменённой записи."""
        collection, model = self._resolve(entity_type)
        with self.__storage.lock:
            self._sync_references()
            target = self.get(entity_type, identifier)
            candidate = self._build(model, data, target)
            targets = self._prepare(collection, candidate, target)
            old_id = target.id
            self.__storage.replace(collection, target, candidate)
            self.__references.update(target.id, targets, old_id)
            self.__revision = self.__storage.revision
            return target

    def delete(self, entity_type: str, identifier: str) -> None:
        """Удалить свободный объект без обхода свойств остальных моделей."""
        collection, _ = self._resolve(entity_type)
        with self.__storage.lock:
            self._sync_references()
            target = self.get(entity_type, identifier)
            self._ensure_not_referenced(target)
            self.__storage.remove(collection, target)
            self.__references.remove(target.id)
            self.__revision = self.__storage.revision
