from abc import ABC, abstractmethod
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class abstract_deserializer(ABC):
    """
    Базовый контракт восстановления доменной модели из словаря JSON.
    """

    def __init__(self, model_type: type[abstract_entity]):
        """
        Инициализация десериализатора с типом восстанавливаемой модели.
        """
        super().__init__()
        if not isinstance(model_type, type) or not issubclass(model_type, abstract_entity):
            raise arguments_exception("Тип модели должен наследовать abstract_entity", "model_type")
        self.__model_type = model_type

    @property
    def model_type(self) -> type[abstract_entity]:
        """
        Получение типа восстанавливаемой доменной модели.
        """
        return self.__model_type

    @abstractmethod
    def deserialize(self, data: dict) -> abstract_entity:
        """
        Восстановление модели и ее идентификатора из словаря JSON.
        """
        pass
