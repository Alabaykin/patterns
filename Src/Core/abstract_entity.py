from abc import ABC
import uuid
from Src.Core.exception import arguments_exception

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

    @id.setter
    def id(self, value: str) -> None:
        """
        Установка id сущности.
        """
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception("Идентификатор должен быть непустой строкой", "id")
        self._id = value.strip()

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
            raise arguments_exception("Имя должно быть непустой строкой", "name")
        self._name = value.strip()

    def __eq__(self, other: object) -> bool:
        """
        Сравнение двух сущностей по идентификатору id.
        """
        if not isinstance(other, abstract_entity):
            return False
        return self.id == other.id

