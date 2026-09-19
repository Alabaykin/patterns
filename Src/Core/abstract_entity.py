from abc import ABC
import uuid


class abstract_entity(ABC):
    """
    Абстрактный базовый класс для сущностей предметной области (имя и id).
    """

    _id: str = None
    _name: str = ""

    @property
    def id(self) -> str:
        """
        Возвращает id сущности.
        Генерируется автоматически при первом обращении.
        """
        if not getattr(self, "_id", None):
            self._id = str(uuid.uuid4())
        return self._id

    @property
    def name(self) -> str:
        """
        Возвращает наименование сущности.
        """
        return getattr(self, "_name", "")

    @name.setter
    def name(self, value: str) -> None:
        """
        Установка наименования.
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise ValueError("Имя должно быть непустой строкой")
        self._name = value.strip()
