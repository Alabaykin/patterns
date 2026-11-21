from dataclasses import dataclass, field
from datetime import datetime, timezone

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_type_enum import filter_type_enum


@dataclass
class filter_item_dto:
    """Условие фильтрации по значению публичного свойства модели."""

    field_name: str
    filter_type: filter_type_enum = filter_type_enum.EQUALS
    value: str = ""

    def __post_init__(self):
        """Проверить поле, строку поиска и вариант сравнения."""
        if self.field_name not in ("name", "id"):
            raise arguments_exception("Фильтрация доступна по name и id", "field_name")
        try:
            self.filter_type = filter_type_enum(self.filter_type)
        except (ValueError, TypeError) as error:
            raise arguments_exception("Ожидается EQUALS или LIKE", "filter_type") from error
        if not isinstance(self.value, str) or not self.value:
            raise arguments_exception("Значение фильтра должно быть непустой строкой", "value")


@dataclass
class filter_dto:
    """Условия фильтрации, применяемые совместно."""

    filters: list[filter_item_dto] = field(default_factory=list)
    recursive: bool = True
    date_from: datetime | None = None
    date_to: datetime | None = None

    def __post_init__(self):
        """Проверить условия и необязательный период количественной ОСВ."""
        if not isinstance(self.filters, list) or any(not isinstance(item, filter_item_dto) for item in self.filters):
            raise arguments_exception("Ожидается список условий фильтрации", "filters")
        if not isinstance(self.recursive, bool):
            raise arguments_exception("Ожидается логическое значение", "recursive")
        self.date_from = self.parse_date(self.date_from, "date_from")
        self.date_to = self.parse_date(self.date_to, "date_to")
        if self.date_from is not None and self.date_to is not None and self.date_from > self.date_to:
            raise arguments_exception("Начало периода позже окончания", "date_from")

    @staticmethod
    def parse_date(value, field_name: str) -> datetime | None:
        """Привести ISO-дату к UTC; дата без часового пояса считается UTC."""
        if value is None:
            return None
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as error:
                raise arguments_exception("Некорректная ISO-дата", field_name) from error
        if not isinstance(value, datetime):
            raise arguments_exception("Ожидается ISO-дата", field_name)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @classmethod
    def from_dict(cls, data: dict) -> "filter_dto":
        """Восстановить DTO запроса без допуска неизвестных полей."""
        if not isinstance(data, dict):
            raise arguments_exception("Ожидается JSON-объект фильтрации", "body")
        if data.keys() - {"filters", "recursive", "date_from", "date_to"}:
            raise arguments_exception("Неизвестное поле DTO фильтрации", "body")
        conditions = data.get("filters", [])
        if not isinstance(conditions, list):
            raise arguments_exception("Ожидается список условий", "filters")
        filters = []
        for item in conditions:
            if not isinstance(item, dict) or item.keys() - {"field_name", "filter_type", "value"}:
                raise arguments_exception("Некорректное условие фильтрации", "filters")
            if "field_name" not in item or "value" not in item:
                raise arguments_exception("Условие требует field_name и value", "filters")
            filters.append(filter_item_dto(**item))
        return cls(filters, data.get("recursive", True), data.get("date_from"), data.get("date_to"))
