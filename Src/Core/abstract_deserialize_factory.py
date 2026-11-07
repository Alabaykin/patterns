from abc import ABC, abstractmethod
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity


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
    def create(self, model_type: type[abstract_entity]) -> abstract_deserializer:
        """
        Подбор десериализатора для указанного типа доменной модели.
        """
        pass

    @abstractmethod
    def deserialize(self, data: object) -> object:
        """
        Восстановление значений из JSON с определением типов вложенных моделей.
        """
        pass
