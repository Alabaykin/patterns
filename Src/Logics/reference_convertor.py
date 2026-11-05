from inspect import getattr_static
from typing import Any
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_convertor import abstract_convertor, _MISSING
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator


class reference_convertor(abstract_convertor):
    """
    Конвертор публичных полей и свойств ссылочных объектов.
    """

    def __init__(self, factory: abstract_convert_factory = None):
        """
        Инициализация конвертора ссылочных типов с фабрикой конверторов.
        """
        super().__init__()
        if factory is None:
            # Локальный импорт исключает циклическую зависимость модулей.
            from Src.Logics.convert_factory import convert_factory
            factory = convert_factory()
        validator.validate(factory, abstract_convert_factory)
        self.__factory = factory

    @property
    def factory(self) -> abstract_convert_factory:
        """
        Получение фабрики для преобразования вложенных значений объекта.
        """
        return self.__factory

    @staticmethod
    def supports(target_type: type) -> bool:
        """
        Проверка возможности извлечения полей и свойств переданного типа.
        """
        return bool(
            getattr(target_type, "__dictoffset__", 0)
            or any("__slots__" in cls.__dict__ for cls in target_type.__mro__)
            or any(isinstance(attr, property)
                   for cls in target_type.__mro__ for attr in cls.__dict__.values())
        )

    def serialize_value(self, value: Any, stack: set = None) -> dict:
        """
        Сериализация ссылочного объекта в словарь публичных полей и свойств.
        """
        if isinstance(value, type) or callable(value) or not self.supports(type(value)):
            raise arguments_exception(
                f"Неподдерживаемый ссылочный тип {type(value).__name__}", "value"
            )
        return self.extract_entity_fields(value, set() if stack is None else stack)

    def convert(self, field_name: Any, value: Any = _MISSING) -> dict:
        """
        Формирование словаря по ссылочному объекту с необязательным именем поля.
        """
        if value is _MISSING:
            return self.serialize_value(field_name)
        field = self._validate_field_name(field_name)
        return {field: self.serialize_value(value)}

    def extract_entity_fields(self, entity: Any, call_stack: set) -> dict:
        """
        Извлечение и сериализация полей объекта с контролем циклических ссылок.
        """
        token = id(entity)
        if token in call_stack:
            if isinstance(entity, abstract_entity):
                return {"id": entity.id, "name": entity.name}
            raise arguments_exception("Циклическая ссылка на объект", "value")

        current_stack = call_stack | {token}
        names = set(getattr(entity, "__dict__", {}))
        for cls in type(entity).__mro__:
            names.update(name for name, attr in cls.__dict__.items()
                         if isinstance(attr, property))
            slots = cls.__dict__.get("__slots__", ())
            names.update((slots,) if isinstance(slots, str) else slots)

        collected = {}
        for name in sorted(names, key=lambda name: (name not in ("id", "name"), name)):
            if name.startswith("_"):
                continue
            # Неинициализированные slots отсутствуют в исходной структуре.
            if not isinstance(getattr_static(type(entity), name, None), property):
                try:
                    value = getattr(entity, name)
                except AttributeError:
                    continue
            else:
                value = getattr(entity, name)
            collected[name] = self.factory.serialize_node(value, current_stack)
        return collected
