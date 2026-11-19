from dataclasses import dataclass, field


@dataclass
class filter_item_dto:
    """Условие фильтрации по значению публичного свойства модели."""

    field_name: str = ""
    filter_type: str = "eq"
    value: object = None


@dataclass
class filter_dto:
    """Условия фильтрации, применяемые совместно."""

    filters: list[filter_item_dto] = field(default_factory=list)
