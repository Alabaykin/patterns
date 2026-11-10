from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class domain_deserializer(abstract_deserializer):
    """
    Общий обработчик вложенных данных для фабричных методов доменных моделей.
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
        Рекурсивное восстановление полей и передача их фабричному методу модели.
        """
        if not isinstance(data, dict):
            raise arguments_exception("Данные модели должны быть словарём", "data")
        model_type = self.model_type
        if data.get("type") != f"{model_type.__module__}.{model_type.__qualname__}":
            raise arguments_exception("Тип JSON не соответствует модели", "type")
        fields = {
            field: self.__factory.deserialize(value)
            for field, value in data.items()
            if field != "type"
        }
        return model_type.from_dict(fields)
