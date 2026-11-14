from dataclasses import dataclass, field

from Src.Dtos.report_field_dto import report_field_dto
from Src.Dtos.report_table_dto import report_table_dto


@dataclass
class report_data_dto:
    """Независимые от формата заголовок, свойства и табличные части отчёта."""

    title: str
    fields: list[report_field_dto] = field(default_factory=list)
    tables: list[report_table_dto] = field(default_factory=list)
