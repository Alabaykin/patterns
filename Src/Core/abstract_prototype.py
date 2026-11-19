from abc import ABC, abstractmethod

from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto


class abstract_prototype(ABC):
    """Базовый прототип для клонирования набора данных."""

    def __init__(self, data: list):
        """Сохранить отдельный список исходных объектов."""
        validator.validate(data, list)
        self._data = data.copy()

    @property
    def data(self) -> list:
        """Данные прототипа."""
        return self._data

    @abstractmethod
    def clone(self, filter: filter_dto) -> "abstract_prototype":
        """Создать прототип с отфильтрованным набором данных."""
        pass
