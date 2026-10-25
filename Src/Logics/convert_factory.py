from datetime import date, datetime
from typing import Any
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor, _MISSING
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor


class convert_factory(abstract_convert_factory):
    """
    Фабрика конвертеров данных.
    Формирует набор словарей согласно структуре переданного объекта,
    используя basic_convertor, datetime_convertor и reference_convertor.
    """
    __converters: dict[type, type[abstract_convertor]] = {}

    def __init__(self):
        """
        Инициализация фабрики конвертеров со стандартным сопоставлением типов.
        """
        super().__init__()
        self.__converters = {
            int: basic_convertor,
            float: basic_convertor,
            str: basic_convertor,
            bool: basic_convertor,
            type(None): basic_convertor,
            datetime: datetime_convertor,
            date: datetime_convertor,
            abstract_entity: reference_convertor,
        }

    @property
    def converters(self) -> dict[type, type[abstract_convertor]]:
        """
        Словарь сопоставления типов данных и классов конверторов.
        """
        return self.__converters

    def create(self, target: Any) -> abstract_convertor:
        """
        Фабричный метод создания экземпляра конвертора для переданного объекта или класса.
        """
        actual_type = target if isinstance(target, type) else type(target)

        if actual_type in self.__converters:
            return self.__converters[actual_type]()

        for registered_type, conv_cls in self.__converters.items():
            if issubclass(actual_type, registered_type):
                return conv_cls()

        raise arguments_exception(
            f"Для типа '{actual_type.__name__}' конвертор не зарегистрирован в фабрике",
            "target"
        )

    def _validate_field_name(self, field_name: str) -> str:
        """
        Валидация наименования поля.
        """
        validator.validate(field_name, str)
        cleaned = field_name.strip()
        if not cleaned:
            raise arguments_exception("Имя поля не может быть пустой строкой", "field_name")
        return cleaned

    def serialize(self, source: Any) -> Any:
        """
        Сериализовать объект любого типа в набор словарей согласно исходной структуре.
        """
        if isinstance(source, (list, tuple, set)):
            return [self.serialize(elem) for elem in source]

        if isinstance(source, dict):
            return {str(k): self.serialize(v) for k, v in source.items()}

        if isinstance(source, abstract_entity):
            conv = self.create(source)
            return conv.convert(source)

        if isinstance(source, (int, float, str, bool, type(None))):
            return source

        if isinstance(source, (datetime, date)):
            conv = self.create(source)
            dt_dict = conv.convert(source)
            return dt_dict.get("datetime", source.isoformat())

        try:
            conv = self.create(source)
            res = conv.convert(source)
            if isinstance(res, dict) and len(res) == 1:
                return next(iter(res.values()))
            return res
        except Exception:
            return str(source)

    def convert(self, target: Any, value: Any = _MISSING) -> Any:
        """
        Преобразование объекта или пары (имя поля, значение) в структуру словарей.
        """
        if value is _MISSING:
            return self.serialize(target)

        field_name = self._validate_field_name(target)

        if isinstance(value, (list, tuple, set)):
            return {field_name: [self.serialize(item) for item in value]}

        if isinstance(value, dict):
            return {field_name: {str(k): self.serialize(v) for k, v in value.items()}}

        conv = self.create(value)
        return conv.convert(field_name, value)
