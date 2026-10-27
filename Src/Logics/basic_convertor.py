from typing import Any
from Src.Core.abstract_convertor import abstract_convertor, _MISSING
from Src.Core.exception import arguments_exception


class basic_convertor(abstract_convertor):
    """
    Конвертор примитивных типов: int, float, str, bool, NoneType.
    """

    ALLOWED_PRIMITIVE_TYPES = (int, float, str, bool)

    def __init__(self):
        """
        Инициализация конвертора простых типов.
        """
        super().__init__()

    def serialize_value(self, value: Any, stack: set = None) -> Any:
        """
        Сериализация простого значения.
        """
        if value is not None and not isinstance(value, self.ALLOWED_PRIMITIVE_TYPES):
            raise arguments_exception(
                f"Значение имеет неподдерживаемый тип {type(value).__name__} для basic_convertor",
                "value"
            )
        return value

    def convert(self, field_name: Any, value: Any = _MISSING) -> dict:
        """
        Формирование словаря по простым типам (numeric, str, bool, None).
        """
        if value is _MISSING:
            val = self.serialize_value(field_name)
            key = "numeric" if isinstance(field_name, (int, float)) else "value"
            return {key: val}

        field = self._validate_field_name(field_name)
        payload = self.serialize_value(value)
        return {field: payload}

