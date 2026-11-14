from urllib.parse import quote
from flask import jsonify

from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.entity_service import entity_service


class entity_controller:
    """HTTP-адаптер сервиса сущностей."""

    def __new__(cls, service: entity_service):
        """Получить единственный экземпляр контроллера."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, service: entity_service):
        """Получить сервис через явную зависимость вместо обращения к глобальному кэшу."""
        if not isinstance(service, entity_service):
            raise arguments_exception("Ожидается сервис сущностей", "service")
        if hasattr(self, "_initialized"):
            return
        self.__service = service
        self.__serializer = convert_factory()
        self._initialized = True

    def list_entities(self, entity_type: str):
        """Вернуть все сущности типа в формате общей сериализации."""
        return jsonify(self.__serializer.serialize(self.__service.list_entities(entity_type)))

    def get_entity(self, entity_type: str, entity_id: str):
        """Вернуть одну сущность по коду."""
        return jsonify(self.__serializer.serialize(self.__service.get(entity_type, entity_id)))

    def create_entity(self, entity_type: str, body: dict):
        """Создать запись через сервис и вернуть JSON, статус 201 и адрес Location."""
        item = self.__service.create(entity_type, body)
        response = jsonify(self.__serializer.serialize(item))
        response.status_code = 201
        response.headers["Location"] = f"/api/entities/{quote(entity_type, safe='')}/{quote(item.id, safe='')}"
        return response

    def update_entity(self, entity_type: str, entity_id: str, body: dict):
        """Передать замену полей сервису и сериализовать обновлённый объект."""
        return jsonify(self.__serializer.serialize(self.__service.update(entity_type, entity_id, body)))

    def delete_entity(self, entity_type: str, entity_id: str):
        """Передать удаление сервису, вернув пустое тело при успехе."""
        self.__service.delete(entity_type, entity_id)
        return "", 204
