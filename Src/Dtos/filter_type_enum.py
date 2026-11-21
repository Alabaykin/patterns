from enum import Enum


class filter_type_enum(Enum):
    """Варианты сравнения строк при фильтрации."""

    EQUALS = "EQUALS"
    LIKE = "LIKE"
