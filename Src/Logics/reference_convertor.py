from datetime import date, datetime
from inspect import ismethod
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor, _MISSING
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class reference_convertor(abstract_convertor):
    """
    Конвертор доменных сущностей.
    """

    def serialize_value(self, value: Any, stack: set = None) -> dict:
        """
        Сериализация сущности в словарь полей.
        """
        if not isinstance(value, abstract_entity):
            raise arguments_exception(
                f"Ожидается сущность abstract_entity, получен {type(value).__name__}",
                "value"
            )
        return self.extract_entity_fields(value, stack or set())

    def convert(self, field_name: Any, value: Any = _MISSING) -> dict:
        """
        Формирование словаря по типу Reference.
        """
        if value is _MISSING:
            if not isinstance(field_name, abstract_entity):
                raise arguments_exception(
                    f"Ожидается сущность abstract_entity, получен {type(field_name).__name__}",
                    "value"
                )
            return self.extract_entity_fields(field_name, set())

        field = self._validate_field_name(field_name)
        payload = self.serialize_value(value, set())
        return {field: payload}

    def _default_serialize_node(self, node: Any, stack: set) -> Any:
        """
        Сериализация произвольного узла при работе без фабрики.
        """
        if isinstance(node, (list, tuple, set)):
            return [self._default_serialize_node(elem, stack) for elem in node]
        if isinstance(node, dict):
            return {str(k): self._default_serialize_node(v, stack) for k, v in node.items()}
        if isinstance(node, (datetime, date)):
            return node.isoformat()
        if isinstance(node, abstract_entity):
            return self.extract_entity_fields(node, stack)
        return node

    def extract_entity_fields(self, entity: abstract_entity, call_stack: set) -> dict:
        """
        Извлечение и сериализация свойств сущности.
        """
        entity_token = f"{entity.__class__.__name__}_{entity.id}"
        if entity_token in call_stack:
            return {"id": entity.id, "name": entity.name}

        current_stack = set(call_stack)
        current_stack.add(entity_token)

        collected: dict[str, Any] = {}
        cls = entity.__class__

        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue

            attr_obj = getattr(cls, attr_name, None)
            if isinstance(attr_obj, property):
                try:
                    attr_val = getattr(entity, attr_name)
                except Exception:
                    continue

                if ismethod(attr_val):
                    continue

                if self._factory is not None:
                    collected[attr_name] = self._factory.serialize_node(attr_val, current_stack)
                else:
                    collected[attr_name] = self._default_serialize_node(attr_val, current_stack)

        sorted_dict = {}
        if "id" in collected:
            sorted_dict["id"] = collected.pop("id")
        if "name" in collected:
            sorted_dict["name"] = collected.pop("name")
        for k in sorted(collected.keys()):
            sorted_dict[k] = collected[k]

        return sorted_dict
