from abc import ABC, abstractmethod
from Src.Core.abstract_deserializer import abstract_deserializer


class abstract_deserialize_factory(ABC):
    """
    Абстрактная фабрика выбора десериализатора по типу доменной модели.
    """

    def __init__(self):
        """
        Инициализация базовой фабрики десериализаторов.
        """
        super().__init__()

    @abstractmethod
    def create(self, type_name: str) -> abstract_deserializer:
        """
        Подбор десериализатора по метке типа из JSON.
        """
        pass

    @abstractmethod
    def deserialize(self, data: object) -> object:
        """
        Восстановление значений из JSON с определением типов вложенных моделей.
        """
        pass
