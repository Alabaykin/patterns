from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_row_deserializer(abstract_deserializer):
    """
    Десериализатор строки рецепта с номенклатурой, единицей измерения и вложенным рецептом.
    """

    def __init__(self, factory: abstract_deserialize_factory):
        """
        Инициализация десериализатора строки с фабрикой обработки вложенных моделей.
        """
        super().__init__(recipe_row_model)
        validator.validate(factory, abstract_deserialize_factory)
        self.__factory = factory

    @property
    def factory(self) -> abstract_deserialize_factory:
        """
        Получение фабрики для восстановления ссылочных полей строки рецепта.
        """
        return self.__factory

    def deserialize(self, data: dict) -> recipe_row_model:
        """
        Восстановление всех полей строки рецепта с рекурсивной обработкой полуфабриката.
        """
        self._validate_data(data, {"id", "name", "nomenclature", "range", "gross", "net", "sub_recipe"})
        nomenclature = self.factory.create(nomenclature_model).deserialize(data["nomenclature"])
        unit = self.factory.create(range_model).deserialize(data["range"])
        sub_recipe = None
        if data["sub_recipe"] is not None:
            sub_recipe = self.factory.create(recipe_model).deserialize(data["sub_recipe"])
        model = recipe_row_model(nomenclature, unit, data["gross"], data["net"], sub_recipe)
        model.name = data["name"]
        return self._restore_id(model, data)
