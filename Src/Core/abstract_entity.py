from abc import ABC
from inspect import getattr_static
import uuid
from typing import Self
from Src.Core.exception import arguments_exception

class abstract_entity(ABC):
    """
    Абстрактный базовый класс для сущностей предметной области (имя и id).
    """

    _id: str = None
    _name: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Создание сущности из восстановленных полей с проверкой записываемых свойств.
        """
        if not isinstance(data, dict):
            raise arguments_exception("Поля модели должны быть словарём", "data")
        if "id" not in data:
            raise arguments_exception("Отсутствует идентификатор модели", "id")

        fields = data.copy()
        model = cls._create_from_fields(fields)
        for field, value in fields.items():
            if not isinstance(field, str) or field.startswith("_"):
                raise arguments_exception("Ожидается имя публичного свойства", str(field))
            attribute = getattr_static(cls, field, None)
            if not isinstance(attribute, property) or attribute.fset is None:
                raise arguments_exception(f"Неизвестное или недоступное для записи поле '{field}'", field)
            setattr(model, field, value)
        return model

    @classmethod
    def _create_from_fields(cls, fields: dict) -> Self:
        """
        Создание именованной модели с извлечением полей, нужных при создании.
        Модель переопределяет метод, если ей требуется дополнительная инициализация.
        """
        return cls(cls._take_required_field(fields, "name"))

    @staticmethod
    def _take_required_field(fields: dict, field: str) -> object:
        """
        Извлечение обязательного поля из рабочей копии данных модели.
        """
        if field not in fields:
            raise arguments_exception("Отсутствует обязательное поле", field)
        return fields.pop(field)

    @property
    def type(self) -> str:
        """
        Полное имя класса модели для восстановления из JSON.
        """
        cls = self.__class__
        return f"{cls.__module__}.{cls.__qualname__}"

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
        elif len(value.strip()) > 50:
            raise arguments_exception("Длина имени не может превышать 50 символов", "name")
        self._name = value.strip()

    def __eq__(self, other: object) -> bool:
        """
        Сравнение двух сущностей по идентификатору id.
        """
        if not isinstance(other, abstract_entity):
            return False
        return self.id == other.id

