import json
from datetime import date, datetime
from typing import Any, Type
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
    Формирует словарь или JSON на основе переданного объекта и зарегистрированных конверторов.
    """

    def __init__(self):
        """
        Инициализация реестра конверторов и кэша экземпляров.
        """
        self._type_registry: dict[type, Type[abstract_convertor]] = {}
        self._cached_converters: dict[Type[abstract_convertor], abstract_convertor] = {}

        self.register_type(int, basic_convertor)
        self.register_type(float, basic_convertor)
        self.register_type(str, basic_convertor)
        self.register_type(bool, basic_convertor)
        self.register_type(type(None), basic_convertor)

        self.register_type(datetime, datetime_convertor)
        self.register_type(date, datetime_convertor)

        self.register_type(abstract_entity, reference_convertor)

    def register_type(self, target_type: type, convertor_class: Type[abstract_convertor]) -> None:
        """
        Регистрация конвертора для конкретного типа данных.
        """
        if not isinstance(target_type, type):
            raise arguments_exception("Регистрируемый target_type должен быть классом", "target_type")

        if not isinstance(convertor_class, type) or not issubclass(convertor_class, abstract_convertor):
            raise arguments_exception("Конвертор должен быть подклассом abstract_convertor", "convertor_class")

        self._type_registry[target_type] = convertor_class

    def get_convertor_for(self, target: Any) -> abstract_convertor:
        """
        Поиск и инстанцирование подходящего конвертора по типу значения или переданному типу.
        """
        actual_type = target if isinstance(target, type) else type(target)

        if actual_type in self._type_registry:
            cls = self._type_registry[actual_type]
            return self._obtain_converter(cls)

        for reg_type, conv_cls in self._type_registry.items():
            if issubclass(actual_type, reg_type):
                return self._obtain_converter(conv_cls)

        raise arguments_exception(
            f"Для типа '{actual_type.__name__}' конвертор не зарегистрирован в фабрике",
            "target"
        )

    def create(self, target: Any) -> abstract_convertor:
        """
        Фабричный метод создания конвертора.
        """
        return self.get_convertor_for(target)

    def _obtain_converter(self, cls: Type[abstract_convertor]) -> abstract_convertor:
        """
        Получение экземпляра с внедрением ссылки на фабрику при наличии поддержки.
        """
        if cls not in self._cached_converters:
            try:
                self._cached_converters[cls] = cls(factory=self)
            except TypeError:
                self._cached_converters[cls] = cls()
        return self._cached_converters[cls]

    def _validate_field_name(self, field_name: str) -> str:
        """
        Валидация имени поля.
        """
        validator.validate(field_name, str)
        cleaned = field_name.strip()
        if not cleaned:
            raise arguments_exception("Имя поля не может быть пустой строкой", "field_name")
        return cleaned

    def convert(self, target: Any, value: Any = _MISSING) -> Any:
        """
        Точка входа конвертации.

        """
        if value is _MISSING:
            return self.serialize_node(target, set())

        field_name = self._validate_field_name(target)

        if isinstance(value, (list, tuple, set)):
            return {field_name: [self.serialize_node(item, set()) for item in value]}

        if isinstance(value, dict):
            return {field_name: {str(k): self.serialize_node(v, set()) for k, v in value.items()}}

        conv = self.get_convertor_for(value)
        return conv.convert(field_name, value)

    def serialize_node(self, node: Any, stack: set) -> Any:
        """
        Рекурсивная обработка произвольного узла структуры данных с использованием
        зарегистрированных конверторов (basic_convertor, datetime_convertor, reference_convertor).
        """
        if isinstance(node, (list, tuple, set)):
            return [self.serialize_node(elem, stack) for elem in node]

        if isinstance(node, dict):
            return {str(k): self.serialize_node(v, stack) for k, v in node.items()}

        try:
            conv = self.get_convertor_for(node)
            return conv.serialize_value(node, stack)
        except Exception:
            return str(node)

    def serialize(self, source: Any) -> Any:
        """
        Сериализовать объект в словарную структуру.
        """
        return self.serialize_node(source, set())

    def to_json(self, source: Any, indent: int = 2) -> str:
        """
        Преобразование объекта в строку JSON.
        """
        payload = self.serialize(source)
        return json.dumps(payload, ensure_ascii=False, indent=indent)

    def dump(self, source: Any, stream, indent: int = 2) -> None:
        """
        Выгрузка сериализованного объекта в файловый поток.
        """
        payload = self.serialize(source)
        json.dump(payload, stream, ensure_ascii=False, indent=indent)
