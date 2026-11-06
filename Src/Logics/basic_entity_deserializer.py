from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity


class basic_entity_deserializer(abstract_deserializer):
    """
    Десериализатор простых справочников с полями id и name.
    Используется для групп и складов.
    """

    def deserialize(self, data: dict) -> abstract_entity:
        """
        Восстановление справочника через конструктор модели с сохранением идентификатора.
        """
        self._validate_data(data, {"id", "name"})
        model = self.model_type(name=data["name"])
        return self._restore_id(model, data)
