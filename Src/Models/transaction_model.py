from datetime import datetime
from math import isfinite
from Src.Core.abstract_entity import abstract_entity
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator


class transaction_model(abstract_entity):
    """Модель транзакции: поступление или списание номенклатуры."""

    __range: range_model = None
    __storage: warehouse_model = None
    __nomenclature: nomenclature_model = None
    __value: float  # + поступление, - списание
    __period: datetime

    def __init__(self, name: str = "Транзакция"):
        """Задать имя записи для хранения в общей коллекции сущностей."""
        self.name = name

    def get_reference_fields(self) -> list[tuple]:
        """Единица измерения, склад и номенклатура складской операции."""
        return [(self, "range"), (self, "storage"), (self, "nomenclature")]

    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, source: range_model) -> None:
        validator.validate(source, range_model)
        self.__range = source

    @property
    def storage(self) -> warehouse_model:
        return self.__storage

    @storage.setter
    def storage(self, source: warehouse_model) -> None:
        validator.validate(source, warehouse_model)
        self.__storage = source

    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, source: nomenclature_model) -> None:
        validator.validate(source, nomenclature_model)
        self.__nomenclature = source

    @property
    def period(self) -> datetime:
        return self.__period

    @period.setter
    def period(self, source: datetime | str) -> None:
        """Принять дату операции или её ISO-представление из JSON."""
        if isinstance(source, str):
            try:
                source = datetime.fromisoformat(source)
            except ValueError as error:
                raise arguments_exception("Некорректная дата операции", "period") from error
        validator.validate(source, datetime)
        self.__period = source

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, source: float) -> None:
        if not isinstance(source, (int, float)) or isinstance(source, bool) or not isfinite(source):
            raise arguments_exception("Количество должно быть конечным числом", "value")
        if source == 0:
            raise arguments_exception("Значение = 0 !")
        self.__value = source
