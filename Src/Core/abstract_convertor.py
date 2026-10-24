from abc import ABC, abstractmethod
from typing import Any
from Src.Core.validator import validator

_MISSING = object()


class abstract_convertor(ABC):
    """
    Базовый контракт конвертора данных.
    """

    def __init__(self, factory=None):
        self._factory = factory

    @property
    def factory(self):
        return self._factory

    @factory.setter
    def factory(self, instance):
        self._factory = instance

    @abstractmethod
    def convert(self, field_name: Any, value: Any = _MISSING) -> dict:
        """
        Абстрактный метод конвертации.
        Принимает любой объект (и по желанию наименование поля) и возвращает словарь:
        ключ - наименование поля, значение - данные поля.
        """
        pass

    def serialize_value(self, value: Any, stack: set = None) -> Any:
        """
        Сериализация значения узла (для рекурсивного обхода).
        """
        pass

    def _validate_field_name(self, field_name: str) -> str:
        """
        Валидация имени поля.
        """
        validator.validate(field_name, str)
        cleaned = field_name.strip()
        if not cleaned:
            raise arguments_exception("Имя поля не может быть пустой строкой", "field_name")
        return cleaned
