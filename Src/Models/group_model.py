from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity


class group_model(abstract_entity):
    """
    Модель группы номенклатуры.
    """
    def __init__(self, name: str):
        """
        Инициализация группы номенклатуры.
        :param name: Наименование группы (до 50 символов)
        """
        self.name = name

    @staticmethod
    def create_raw() -> group_model:
        """
        Фабричный метод создания группы 'Сырье'.
        """
        return group_model("Сырье")

    @staticmethod
    def create_semi() -> group_model:
        """
        Фабричный метод создания группы 'Полуфабрикаты'.
        """
        return group_model("Полуфабрикаты")

    @staticmethod
    def create_dishes() -> group_model:
        """
        Фабричный метод создания группы 'Блюда'.
        """
        return group_model("Блюда")

    @staticmethod
    def create_package() -> group_model:
        """
        Фабричный метод создания группы 'Упаковка'.
        """
        return group_model("Упаковка")
