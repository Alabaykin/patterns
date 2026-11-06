from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.validator import validator
from Src.Models.range_model import range_model


class range_deserializer(abstract_deserializer):
    """
    Десериализатор единиц измерения с рекурсивным восстановлением базовой единицы.
    """

    def __init__(self, factory: abstract_deserialize_factory):
        """
        Инициализация десериализатора с фабрикой обработки вложенных моделей.
        """
        super().__init__(range_model)
        validator.validate(factory, abstract_deserialize_factory)
        self.__factory = factory

    @property
    def factory(self) -> abstract_deserialize_factory:
        """
        Получение фабрики для восстановления вложенной базовой единицы измерения.
        """
        return self.__factory

    def deserialize(self, data: dict) -> range_model:
        """
        Восстановление единицы измерения, коэффициента и вложенной цепочки базовых единиц.
        """
        self._validate_data(data, {"id", "name", "coefficient", "base_range"})
        base_range = None
        if data["base_range"] is not None:
            deserializer = self.factory.create(range_model)
            base_range = deserializer.deserialize(data["base_range"])
        model = range_model(data["name"], data["coefficient"], base_range)
        return self._restore_id(model, data)
