from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Dtos.filter_type_enum import filter_type_enum


class prototype(abstract_prototype):
    """Прототип набора данных с фильтрацией при клонировании."""

    def clone(self, filter: filter_dto) -> "prototype":
        """Создать отдельный список, сохраняя ссылки на исходные модели."""
        validator.validate(filter, filter_dto)
        filter.__post_init__()
        result = prototype(self._data)

        # Проверить условия до обхода: ошибки не зависят от наличия данных.
        for condition in filter.filters:
            validator.validate(condition, filter_item_dto)
            condition.__post_init__()
        result._data = [item for item in result._data if self._matches(item, filter)]
        return result

    @staticmethod
    def _matches(source: abstract_entity, filter: filter_dto) -> bool:
        """Проверить все условия по модели и, при необходимости, её зависимостям."""
        if not isinstance(source, abstract_entity):
            raise arguments_exception("Ожидается доменная модель", "data")
        pending = [source]
        visited = set()
        matched = set()
        while pending:
            item = pending.pop()
            if id(item) in visited:
                continue
            visited.add(id(item))
            for number, condition in enumerate(filter.filters):
                value = getattr(item, condition.field_name)
                if condition.filter_type is filter_type_enum.EQUALS:
                    success = value == condition.value
                else:
                    success = condition.value in value
                if success:
                    matched.add(number)
            if len(matched) == len(filter.filters):
                return True
            if filter.recursive:
                pending.extend(item.get_references())
        return False
