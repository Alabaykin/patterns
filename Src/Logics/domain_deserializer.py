from inspect import Parameter, getattr_static, signature
from typing import get_origin, get_type_hints
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class domain_deserializer(abstract_deserializer):
    """
    Общий обработчик доменных моделей с рефлексией параметров конструктора.
    """

    def __init__(
        self, model_type: type[abstract_entity], factory: abstract_deserialize_factory
    ):
        """
        Инициализация обработчика выбранной модели и её вложенных данных.
        """
        super().__init__(model_type)
        if not isinstance(factory, abstract_deserialize_factory):
            raise arguments_exception("Ожидается фабрика десериализаторов", "factory")
        self.__factory = factory

    def deserialize(self, data: dict) -> abstract_entity:
        """
        Восстановление аргументов конструктора и остальных записываемых свойств.
        """
        if not isinstance(data, dict):
            raise arguments_exception("Данные модели должны быть словарём", "data")
        model_type = self.model_type
        if data.get("type") != f"{model_type.__module__}.{model_type.__qualname__}":
            raise arguments_exception("Тип JSON не соответствует модели", "type")
        if "id" not in data:
            raise arguments_exception("Отсутствует идентификатор модели", "id")

        constructor = signature(model_type)
        field_types = get_type_hints(model_type.__init__)
        arguments = {}
        properties = {}

        for field, value in data.items():
            if field == "type":
                continue
            if field in constructor.parameters:
                if get_origin(field_types.get(field)) is list and not isinstance(value, list):
                    raise arguments_exception("Ожидается список", field)
                arguments[field] = self.__factory.deserialize(value)
                continue
            attribute = getattr_static(self.model_type, field, None)
            if field.startswith("_") or not isinstance(attribute, property) or attribute.fset is None:
                raise arguments_exception(f"Неизвестное или недоступное для записи поле '{field}'", field)
            properties[field] = self.__factory.deserialize(value)

        for parameter in constructor.parameters.values():
            if (
                parameter.kind in (Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY)
                and parameter.default is Parameter.empty
                and parameter.name not in arguments
            ):
                raise arguments_exception("Отсутствует обязательное поле", parameter.name)

        try:
            constructor.bind(**arguments)
        except TypeError as error:
            raise arguments_exception(str(error), "data") from error

        model = self.model_type(**arguments)
        for field, value in properties.items():
            setattr(model, field, value)
        return model
