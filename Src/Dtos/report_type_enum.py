from enum import Enum

"""
Типы отчетов
"""
class report_type_enum(Enum):
    TXT = 1
    MARKDOWN = 2
    CSV = 3
    XML = 4
    HTML = 5

    """
    Преобразование строки в элемент перечисления
    """
    @classmethod
    def from_string(cls, value: str):
        if not isinstance(value, str):
            return None
        val_upper = value.strip().upper()
        if val_upper == "MD":
            val_upper = "MARKDOWN"
        try:
            return cls[val_upper]
        except KeyError:
            return None
