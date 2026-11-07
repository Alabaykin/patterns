from inspect import getattr_static, signature
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
        self.__factory = factory

    def deserialize(self, data: dict) -> abstract_entity:
        """
        Восстановление аргументов конструктора и остальных записываемых свойств.
        """
        constructor = signature(self.model_type)
        arguments = {}
        properties = {}

        for field, value in data.items():
            if field == "type":
                continue
            if field in constructor.parameters:
                arguments[field] = self.__factory.deserialize(value)
                continue
            attribute = getattr_static(self.model_type, field, None)
            if field.startswith("_") or not isinstance(attribute, property) or attribute.fset is None:
                raise arguments_exception(f"Неизвестное или недоступное для записи поле '{field}'", field)
            properties[field] = self.__factory.deserialize(value)

        try:
            constructor.bind(**arguments)
        except TypeError as error:
            raise arguments_exception(str(error), "data") from error

        model = self.model_type(**arguments)
        for field, value in properties.items():
            setattr(model, field, value)
        return model
