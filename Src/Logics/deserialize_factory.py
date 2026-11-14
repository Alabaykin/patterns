from Src import Models
from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.domain_deserializer import domain_deserializer
from Src.Logics.convert_factory import convert_factory
from uuid import uuid4
from collections.abc import Mapping


class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика подбора общего обработчика по типу модели из JSON.
    """

    def __init__(self, references: Mapping[str, abstract_entity] | None = None):
        """
        Построение словаря разрешённых типов из публичных моделей пакета Src.Models.
        """
        super().__init__()
        self.__references = references
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
            if self.__references is not None:
                if "id" in data:
                    identifier = data["id"]
                    if not isinstance(identifier, str) or not identifier.strip():
                        raise arguments_exception("Ожидается непустой код ссылки", "id")
                    source = self.__references.get(identifier.strip())
                    if source is not None:
                        if data.keys() <= {"id", "type"}:
                            if data.get("type", source.type) != source.type:
                                raise arguments_exception("Тип ссылки не соответствует сущности", "type")
                        elif data != convert_factory().serialize(source):
                            raise arguments_exception("Изменяйте связанную сущность отдельной операцией", "id")
                        return source
                    if data.keys() <= {"id", "type"}:
                        raise arguments_exception(f"Не найдена сущность по ссылке '{identifier}'", "id")
                if "type" in data and "id" not in data:
                    data = {**data, "id": str(uuid4())}
            if "type" not in data:
                return {key: self.deserialize(value) for key, value in data.items()}
            return self.create(data["type"]).deserialize(data)
        if data is None or isinstance(data, (bool, int, float, str)):
            return data
        raise arguments_exception("Ожидаются данные из JSON", "data")
