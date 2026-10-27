from abc import ABC, abstractmethod
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor, _MISSING


class abstract_convert_factory(ABC):
    """
    Абстрактная фабрика конвертеров.
    Задает стандартный интерфейс порождения конвертеров и сериализации структур данных.
    """

    def __init__(self):
        """
        Инициализация базовой абстрактной фабрики.
        """
        super().__init__()

    @abstractmethod
    def create(self, target: Any) -> abstract_convertor:
        """
        Фабричный метод создания конвертора для переданного объекта или класса.
        """
        pass

    @abstractmethod
    def convert(self, target: Any, value: Any = _MISSING) -> Any:
        """
        Преобразование объекта или свойства в структуру словарей.
        """
        pass

    @abstractmethod
    def serialize(self, source: Any) -> Any:
        """
        Сериализация переданного объекта.
        """
        pass

