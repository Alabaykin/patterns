from inspect import getmembers
from typing import get_args, get_origin, get_type_hints
from Src.Core.abstract_entity import abstract_entity


class entity_registry:
    """Определяет коллекции и модели по аннотациям свойств хранилища."""

    @staticmethod
    def get_models(storage_type: type) -> dict[str, type]:
        """Собрать свойства вида list[модель]."""
        models = {}
        for name, attribute in getmembers(storage_type):
            if not isinstance(attribute, property) or attribute.fget is None:
                continue
            annotation = get_type_hints(attribute.fget).get("return")
            if get_origin(annotation) is not list:
                continue
            model, = get_args(annotation)
            if isinstance(model, type) and model is not abstract_entity and issubclass(model, abstract_entity):
                models[name] = model
        return models
