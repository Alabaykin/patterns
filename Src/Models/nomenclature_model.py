from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


class nomenclature_model(abstract_entity):
    """
    Модель номенклатуры (сырье, блюдо, полуфабрикат, товар).
    """
    _full_name: str = ""
    _group: group_model = None
    _range: range_model = None

    def __init__(self, name: str, full_name: str, group: group_model, range: range_model):
        """
        Инициализация номенклатуры.
        :param name: Краткое наименование (до 50 символов)
        :param full_name: Полное наименование (до 255 символов)
        :param group: Группа номенклатуры (group_model)
        :param range: Единица измерения (range_model)
        """
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self) -> str:
        """
        Полное наименование номенклатуры (до 255 символов).
        """
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """
        Установка полного наименования.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Полное наименование должно быть непустой строкой", "full_name")
        if len(value.strip()) > 255:
            raise arguments_exception("Полное наименование не должно превышать 255 символов", "full_name")
        self._full_name = value.strip()

    @property
    def group(self) -> group_model:
        """
        Группа номенклатуры.
        """
        return self._group

    @group.setter
    def group(self, value: group_model) -> None:
        """
        Установка группы номенклатуры.
        """
        if not isinstance(value, group_model):
            raise arguments_exception("Группа номенклатуры должна быть объектом group_model", "group")
        self._group = value

    @property
    def range(self) -> range_model:
        """
        Единица измерения номенклатуры.
        """
        return self._range

    @range.setter
    def range(self, value: range_model) -> None:
        """
        Установка единицы измерения номенклатуры.
        """
        if not isinstance(value, range_model):
            raise arguments_exception("Единица измерения должна быть объектом range_model", "range")
        self._range = value

    @staticmethod
    def create_flour() -> nomenclature_model:
        """Фабричный метод номенклатуры: Мука пшеничная"""
        return nomenclature_model(
            name="Мука пшеничная",
            full_name="Мука пшеничная высший сорт",
            group=group_model.create_raw(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_sugar() -> nomenclature_model:
        """Фабричный метод номенклатуры: Сахар-песок"""
        return nomenclature_model(
            name="Сахар",
            full_name="Сахар-песок белый",
            group=group_model.create_raw(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_butter() -> nomenclature_model:
        """Фабричный метод номенклатуры: Сливочное масло"""
        return nomenclature_model(
            name="Сливочное масло",
            full_name="Масло сливочное 82.5%",
            group=group_model.create_raw(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_egg() -> nomenclature_model:
        """Фабричный метод номенклатуры: Яйцо куриное"""
        return nomenclature_model(
            name="Яйцо куриное",
            full_name="Яйцо куриное категории С0",
            group=group_model.create_raw(),
            range=range_model.create_piece()
        )

    @staticmethod
    def create_vanilla() -> nomenclature_model:
        """Фабричный метод номенклатуры: Ванилин"""
        return nomenclature_model(
            name="Ванилин",
            full_name="Ванилин кристаллический",
            group=group_model.create_raw(),
            range=range_model.create_gramm()
        )

    @staticmethod
    def create_condensed_milk() -> nomenclature_model:
        """Фабричный метод номенклатуры: Сгущенное молоко"""
        return nomenclature_model(
            name="Молоко сгущенное вареное",
            full_name="Молоко сгущенное вареное цельное",
            group=group_model.create_raw(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_shortcrust_dough() -> nomenclature_model:
        """Фабричный метод номенклатуры: Песочное тесто (полуфабрикат)"""
        return nomenclature_model(
            name="Песочное тесто",
            full_name="Тесто песочное полуфабрикат",
            group=group_model.create_semi(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_cream() -> nomenclature_model:
        """Фабричный метод номенклатуры: Крем со сгущенкой (полуфабрикат)"""
        return nomenclature_model(
            name="Крем со сгущенкой",
            full_name="Крем масляный со сгущенным молоком полуфабрикат",
            group=group_model.create_semi(),
            range=range_model.create_kilogramm()
        )

    @staticmethod
    def create_waffle_cake() -> nomenclature_model:
        """Фабричный метод номенклатуры: Вафельный торт (готовое блюдо)"""
        return nomenclature_model(
            name="Вафельный торт",
            full_name="Торт песочно-вафельный с кремом",
            group=group_model.create_dishes(),
            range=range_model.create_piece()
        )

    @staticmethod
    def create_cake_box() -> nomenclature_model:
        """Фабричный метод номенклатуры: Коробка для торта (упаковка)"""
        return nomenclature_model(
            name="Коробка для торта",
            full_name="Картонная коробка самосборная 25х25х15 см",
            group=group_model.create_package(),
            range=range_model.create_piece()
        )
