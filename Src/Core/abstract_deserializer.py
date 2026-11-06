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

    def _validate_data(self, data: dict, fields: set[str]) -> None:
        """
        Проверка структуры словаря и наличия всех полей сериализованной модели.
        """
        if not isinstance(data, dict):
            raise arguments_exception("Данные модели должны быть словарем", "data")
        missing = fields - data.keys()
        if missing:
            field = sorted(missing)[0]
            raise arguments_exception(f"Отсутствует обязательное поле '{field}'", field)
        unexpected = data.keys() - fields
        if unexpected:
            field = str(next(iter(unexpected)))
            raise arguments_exception(f"Неизвестное поле модели '{field}'", field)

    def _restore_id(self, model: abstract_entity, data: dict) -> abstract_entity:
        """
        Восстановление исходного идентификатора через проверку свойства модели.
        """
        model.id = data["id"]
        return model
