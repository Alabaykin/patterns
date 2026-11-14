from dataclasses import dataclass


@dataclass
class report_field_dto:
    """Имя свойства и его текстовое представление для отчёта."""

    name: str
    value: str
