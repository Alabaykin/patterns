from Src.Core.abstract_prototype import abstract_prototype
from Src.Core.exception import arguments_exception
from Src.Core.validator import validator
from Src.Dtos.filter_dto import filter_dto, filter_item_dto


class prototype(abstract_prototype):
    """Прототип набора данных с фильтрацией при клонировании."""

    def clone(self, filter: filter_dto) -> "prototype":
        """Создать отдельный список, сохраняя ссылки на исходные модели."""
        validator.validate(filter, filter_dto)
        validator.validate(filter.filters, list)
        result = prototype(self._data)

        # Фильтрация
        for condition in filter.filters:
            validator.validate(condition, filter_item_dto)
            validator.validate(condition.field_name, str)
            if condition.field_name.startswith("_"):
                raise arguments_exception("Ожидается публичное свойство модели", "field_name")
            if condition.filter_type != "eq":
                raise arguments_exception("Поддерживается только фильтр eq", "filter_type")

            items = []
            for item in result._data:
                if not hasattr(item, condition.field_name):
                    raise arguments_exception("Свойство модели не найдено", condition.field_name)
                if getattr(item, condition.field_name) == condition.value:
                    items.append(item)
            result._data = items

        return result
