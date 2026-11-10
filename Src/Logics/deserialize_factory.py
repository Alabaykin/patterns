from Src import Models
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.domain_deserializer import domain_deserializer


class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика подбора общего обработчика по типу модели из JSON.
    """

    def __init__(self):
        """
        Построение словаря разрешённых типов из публичных моделей пакета Src.Models.
        """
        super().__init__()
        model_types = (getattr(Models, name) for name in Models.__all__)
        self.__model_types = {
            f"{model_type.__module__}.{model_type.__qualname__}": model_type
            for model_type in model_types
            if isinstance(model_type, type) and issubclass(model_type, abstract_entity)
        }

    def create(self, type_name: str) -> abstract_deserializer:
        """
        Создание общего обработчика для модели, указанной в метке типа.
        """
        if not isinstance(type_name, str) or type_name not in self.__model_types:
            raise arguments_exception("Неизвестный тип доменной модели", "type")
        return domain_deserializer(self.__model_types[type_name], self)

    def deserialize(self, data: object) -> object:
        """
        Восстановление модели по метке типа и рекурсивный обход коллекций JSON.
        """
        if isinstance(data, list):
            return [self.deserialize(item) for item in data]
        if isinstance(data, dict):
            if "type" not in data:
                return {key: self.deserialize(value) for key, value in data.items()}
            return self.create(data["type"]).deserialize(data)
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        raise arguments_exception("Ожидаются данные из JSON", "data")
