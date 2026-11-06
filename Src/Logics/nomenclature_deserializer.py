from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.validator import validator
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class nomenclature_deserializer(abstract_deserializer):
    """
    Десериализатор номенклатуры с восстановлением группы и единицы измерения.
    """

    def __init__(self, factory: abstract_deserialize_factory):
        """
        Инициализация десериализатора номенклатуры с фабрикой вложенных моделей.
        """
        super().__init__(nomenclature_model)
        validator.validate(factory, abstract_deserialize_factory)
        self.__factory = factory

    @property
    def factory(self) -> abstract_deserialize_factory:
        """
        Получение фабрики для восстановления ссылочных полей номенклатуры.
        """
        return self.__factory

    def deserialize(self, data: dict) -> nomenclature_model:
        """
        Восстановление номенклатуры, ее идентификатора и вложенных справочников.
        """
        self._validate_data(data, {"id", "name", "full_name", "group", "range"})
        group = self.factory.create(group_model).deserialize(data["group"])
        unit = self.factory.create(range_model).deserialize(data["range"])
        model = nomenclature_model(data["name"], data["full_name"], group, unit)
        return self._restore_id(model, data)
