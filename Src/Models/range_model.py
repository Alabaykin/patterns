from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class range_model(abstract_entity):
    """
    Модель единицы измерения.
    """
    _coefficient: float = 1.0
    _base_range: range_model = None

    def __init__(self, name: str, coefficient: float = 1.0, base_range: range_model = None):
        """
        Инициализация единицы измерения.
        :param name: Наименование единицы измерения (до 50 символов)
        :param coefficient: Коэффициент пересчета относительно базовой единицы (> 0)
        :param base_range: Базовая единица измерения (если None, ссылается на саму себя)
        """
        self.name = name
        self.coefficient = coefficient
        self.base_range = base_range if base_range is not None else self

    @property
    def coefficient(self) -> float:
        """
        Коэффициент пересчета относительно базовой единицы.
        """
        return self._coefficient

    @coefficient.setter
    def coefficient(self, value: float) -> None:
        """
        Установка коэффициента пересчета.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Коэффициент должен быть числом", "coefficient")
        if value <= 0:
            raise arguments_exception("Коэффициент должен быть положительным числом", "coefficient")
        self._coefficient = float(value)

    @property
    def base_range(self) -> range_model:
        """
        Базовая единица измерения.
        """
        return self._base_range

    @base_range.setter
    def base_range(self, value: range_model) -> None:
        """
        Установка базовой единицы измерения.
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("Базовая единица измерения должна быть объектом range_model", "base_range")
        self._base_range = value if value is not None else self

    def to_base(self, value: float) -> float:
        """
        Пересчет количества текущей единицы в базовую единицу.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Значение для пересчета должно быть числом", "value")
        return value * self.coefficient

