from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model


class recipe_deserializer(abstract_deserializer):
    """
    Десериализатор рецепта со строками ингредиентов и вложенными справочниками.
    """

    def __init__(self, factory: abstract_deserialize_factory):
        """
        Инициализация десериализатора рецепта с фабрикой обработки вложенных моделей.
        """
        super().__init__(recipe_model)
        validator.validate(factory, abstract_deserialize_factory)
        self.__factory = factory

    @property
    def factory(self) -> abstract_deserialize_factory:
        """
        Получение фабрики для восстановления строк и ссылочных полей рецепта.
        """
        return self.__factory

    def deserialize(self, data: dict) -> recipe_model:
        """
        Восстановление рецепта, его строк, инструкции и параметров готового изделия.
        """
        self._validate_data(data, {"id", "name", "rows", "steps", "output_range", "target_nomenclature"})
        if not isinstance(data["rows"], list):
            raise arguments_exception("Строки рецепта должны быть списком", "rows")
        rows = [self.factory.create(recipe_row_model).deserialize(row) for row in data["rows"]]
        output_range = None
        if data["output_range"] is not None:
            output_range = self.factory.create(range_model).deserialize(data["output_range"])
        target_nomenclature = None
        if data["target_nomenclature"] is not None:
            target_nomenclature = self.factory.create(nomenclature_model).deserialize(data["target_nomenclature"])
        model = recipe_model(data["name"], rows, data["steps"], output_range, target_nomenclature)
        return self._restore_id(model, data)
