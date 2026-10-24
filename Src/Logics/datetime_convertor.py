from datetime import date, datetime
from typing import Any
from Src.Core.abstract_convertor import abstract_convertor, _MISSING
from Src.Core.exception import arguments_exception


class datetime_convertor(abstract_convertor):
    """
    Конвертор дат и времени в строковый формат ISO.
    """

    def serialize_value(self, value: Any, stack: set = None) -> str:
        """
        Сериализация даты/времени в формат ISO.
        """
        if not isinstance(value, (datetime, date)):
            raise arguments_exception(
                f"Ожидается тип datetime/date, получен {type(value).__name__}",
                "value"
            )
        return value.isoformat()

    def convert(self, field_name: Any, value: Any = _MISSING) -> dict:
        """
        Формирование словаря по типу DateTime.
        """
        if value is _MISSING:
            val = self.serialize_value(field_name)
            return {"datetime": val}

        field = self._validate_field_name(field_name)
        payload = self.serialize_value(value)
        return {field: payload}
