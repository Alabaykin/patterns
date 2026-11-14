from dataclasses import dataclass, field


@dataclass
class report_table_dto:
    """Табличная часть: путь коллекции, колонки и все строки значений."""

    name: str
    columns: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
