from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.validator import validator
from Src.Core.exception import arguments_exception
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_row_model(abstract_entity):
    """
    Модель строки рецепта.
    Представляет отдельный ингредиент в рецепте.
    """
    _nomenclature: nomenclature_model = None
    _range: range_model = None
    _gross: float = 0.0
    _net: float = 0.0

    def __init__(self, nomenclature: nomenclature_model, range: range_model, gross: float, net: float):
        """
        Инициализация строки рецепта.
        :param nomenclature: Номенклатура ингредиента (сырье, полуфабрикат, упаковка)
        :param range: Единица измерения
        :param gross: Вес/количество брутто (> 0)
        :param net: Вес/количество нетто (> 0)
        """
        self.nomenclature = nomenclature
        self.range = range
        self.gross = gross
        self.net = net
        self.name = nomenclature.name

    @property
    def nomenclature(self) -> nomenclature_model:
        """
        Номенклатура ингредиента.
        """
        return self._nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        validator.validate(value, nomenclature_model)
        self._nomenclature = value

    @property
    def range(self) -> range_model:
        """
        Единица измерения ингредиента.
        """
        return self._range

    @range.setter
    def range(self, value: range_model) -> None:
        validator.validate(value, range_model)
        self._range = value

    @property
    def gross(self) -> float:
        """
        Вес/количество брутто.
        """
        return self._gross

    @gross.setter
    def gross(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Вес брутто должен быть числом", "gross")
        if value <= 0:
            raise arguments_exception("Вес брутто должен быть положительным числом", "gross")
        self._gross = float(value)

    @property
    def net(self) -> float:
        """
        Вес/количество нетто.
        """
        return self._net

    @net.setter
    def net(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise arguments_exception("Вес нетто должен быть числом", "net")
        if value <= 0:
            raise arguments_exception("Вес нетто должен быть положительным числом", "net")
        self._net = float(value)

    @staticmethod
    def create_flour_row(gross: float = 0.250, net: float = 0.250) -> recipe_row_model:
        """Фабричный метод строки рецепта: Мука пшеничная"""
        flour = nomenclature_model.create_flour()
        return recipe_row_model(flour, flour.range, gross, net)

    @staticmethod
    def create_sugar_row(gross: float = 0.150, net: float = 0.150) -> recipe_row_model:
        """Фабричный метод строки рецепта: Сахар"""
        sugar = nomenclature_model.create_sugar()
        return recipe_row_model(sugar, sugar.range, gross, net)

    @staticmethod
    def create_butter_row(gross: float = 0.100, net: float = 0.100) -> recipe_row_model:
        """Фабричный метод строки рецепта: Сливочное масло"""
        butter = nomenclature_model.create_butter()
        return recipe_row_model(butter, butter.range, gross, net)

    @staticmethod
    def create_egg_row(gross: float = 2.0, net: float = 2.0) -> recipe_row_model:
        """Фабричный метод строки рецепта: Яйцо куриное"""
        egg = nomenclature_model.create_egg()
        return recipe_row_model(egg, egg.range, gross, net)

    @staticmethod
    def create_vanilla_row(gross: float = 2.0, net: float = 2.0) -> recipe_row_model:
        """Фабричный метод строки рецепта: Ванилин"""
        vanilla = nomenclature_model.create_vanilla()
        return recipe_row_model(vanilla, vanilla.range, gross, net)

    @staticmethod
    def create_condensed_milk_row(gross: float = 0.200, net: float = 0.200) -> recipe_row_model:
        """Фабричный метод строки рецепта: Молоко сгущенное вареное"""
        condensed_milk = nomenclature_model.create_condensed_milk()
        return recipe_row_model(condensed_milk, condensed_milk.range, gross, net)

    @staticmethod
    def create_dough_row(gross: float = 0.550, net: float = 0.550) -> recipe_row_model:
        """Фабричный метод строки рецепта: Песочное тесто (полуфабрикат)"""
        dough = nomenclature_model.create_shortcrust_dough()
        return recipe_row_model(dough, dough.range, gross, net)

    @staticmethod
    def create_cream_row(gross: float = 0.300, net: float = 0.300) -> recipe_row_model:
        """Фабричный метод строки рецепта: Крем со сгущенкой (полуфабрикат)"""
        cream = nomenclature_model.create_cream()
        return recipe_row_model(cream, cream.range, gross, net)

    @staticmethod
    def create_box_row(gross: float = 1.0, net: float = 1.0) -> recipe_row_model:
        """Фабричный метод строки рецепта: Коробка для торта (упаковка)"""
        box = nomenclature_model.create_cake_box()
        return recipe_row_model(box, box.range, gross, net)
