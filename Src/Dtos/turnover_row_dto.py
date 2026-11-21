from dataclasses import dataclass

from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.warehouse_model import warehouse_model


@dataclass
class turnover_row_dto:
    """Строка количественной оборотно-сальдовой ведомости."""

    nomenclature: nomenclature_model
    storage: warehouse_model
    range: range_model
    opening_balance: float = 0.0
    receipt: float = 0.0
    expense: float = 0.0
    closing_balance: float = 0.0
