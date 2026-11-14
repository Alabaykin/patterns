from datetime import date, datetime
from enum import Enum
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
            Enum: basic_convertor,
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
            return self._instantiate(self.__converters[actual_type])

        for registered_type, conv_cls in self.__converters.items():
            if issubclass(actual_type, registered_type):
                return self._instantiate(conv_cls)

        if reference_convertor.supports(actual_type) and not callable(target) and not isinstance(target, type):
            return reference_convertor(self)

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

    def _instantiate(self, converter_type: type[abstract_convertor]) -> abstract_convertor:
        """
        Создание конвертора с передачей фабрики ссылочному конвертору.
        """
        if issubclass(converter_type, reference_convertor):
            return converter_type(self)
        return converter_type()

    def serialize(self, source: Any) -> Any:
        """
        Сериализовать объект любого типа в набор словарей согласно исходной структуре.
        """
        return self.serialize_node(source, set())

    def serialize_node(self, source: Any, stack: set) -> Any:
        """
        Общий обход структуры с контролем циклов на текущем пути.
        """
        if isinstance(source, (list, tuple, set, dict)):
            token = id(source)
            if token in stack:
                raise arguments_exception("Циклическая ссылка на коллекцию", "value")
            current_stack = stack | {token}
            if isinstance(source, dict):
                result = {}
                for key, value in source.items():
                    field = str(key)
                    if field in result:
                        raise arguments_exception("Ключи словаря совпали после преобразования в строку", "value")
                    result[field] = self.serialize_node(value, current_stack)
                return result
            return [self.serialize_node(item, current_stack) for item in source]
        return self.create(source).serialize_value(source, stack)

    def convert(self, target: Any, value: Any = _MISSING) -> Any:
        """
        Преобразование объекта или пары (имя поля, значение) в структуру словарей.
        """
        if value is _MISSING:
            return self.serialize(target)

        field_name = self._validate_field_name(target)

        return {field_name: self.serialize(value)}
