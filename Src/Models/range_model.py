from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception, operation_exception


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
        :param base_range: Базовая единица измерения (если None, то текущая единица является базовой)
        """
        self.name = name
        self.coefficient = coefficient
        self.base_range = base_range

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
        Базовая единица измерения (None для базовых единиц).
        """
        return self._base_range

    @base_range.setter
    def base_range(self, value: range_model) -> None:
        """
        Установка базовой единицы измерения.
        """
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception("Базовая единица измерения должна быть объектом range_model", "base_range")
        self._base_range = value

    @property
    def base(self) -> range_model:
        """
        Алиас для базовой единицы измерения.
        """
        return self._base_range

    def to_base(self, value: float) -> float:
        """
        Пересчет количества текущей единицы в базовую единицу.
        """
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Значение для пересчета должно быть числом", "value")
        return value * self.coefficient

    def convert_to(self, target: range_model, value: float) -> float:
        """
        Пересчет значения текущей единицы измерения в целевую совместимую единицу.
        """
        if not isinstance(target, range_model):
            raise arguments_exception("Целевая единица должна быть объектом range_model", "target")
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Значение для пересчета должно быть числом", "value")

        # Определяем базовую единицу для каждого (если base_range None, базовой является сама единица)
        self_root = self.base_range if self.base_range is not None else self
        target_root = target.base_range if target.base_range is not None else target

        if self_root != target_root:
            raise operation_exception(
                f"Невозможно выполнить пересчет из '{self.name}' в '{target.name}': разные базовые единицы измерения"
            )

        base_val = self.to_base(value)
        return base_val / target.coefficient

    @staticmethod
    def create_kilogramm():
        """
        Фабричный метод
        """

        gramm = range_model(name="Грамм")
        result = range_model(name="Килограмм", coefficient=1000.0, base_range=gramm)
        return result

