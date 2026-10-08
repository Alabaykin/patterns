from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity


class warehouse_model(abstract_entity):
    """
    Модель склада.
    """
    def __init__(self, name: str):
        """
        Инициализация склада.
        :param name: Наименование склада (до 50 символов)
        """
        self.name = name

    @staticmethod
    def create_main() -> warehouse_model:
        """
        Фабричный метод создания 'Основной склад'.
        """
        return warehouse_model("Основной склад")

    @staticmethod
    def create_kitchen() -> warehouse_model:
        """
        Фабричный метод создания склада 'Кухня'.
        """
        return warehouse_model("Кухня")

    @staticmethod
    def create_delivery() -> warehouse_model:
        """
        Фабричный метод создания склада 'Зона доставки'.
        """
        return warehouse_model("Зона доставки")
