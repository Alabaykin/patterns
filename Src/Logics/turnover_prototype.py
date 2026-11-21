from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto
from Src.Dtos.turnover_row_dto import turnover_row_dto
from Src.Logics.prototype import prototype
from Src.Models.transaction_model import transaction_model


class turnover_prototype(prototype):
    """Прототип количественной ОСВ на основе отфильтрованных транзакций."""

    def __init__(self, data: list):
        """Сохранить операции, по которым можно повторно клонировать ведомость."""
        super().__init__(data)
        self.__transactions = self._data

    def clone(self, filter: filter_dto) -> "turnover_prototype":
        """Сформировать отдельную ведомость, не изменяя исходные операции."""
        transactions = prototype(self.__transactions).clone(filter).data
        rows = {}
        for transaction in transactions:
            if not isinstance(transaction, transaction_model):
                raise arguments_exception("ОСВ строится по транзакциям", "data")
            period = filter.parse_date(transaction.period, "period")
            if filter.date_to is not None and period > filter.date_to:
                continue
            key = (transaction.storage.id, transaction.nomenclature.id, transaction.range.id)
            if key not in rows:
                rows[key] = turnover_row_dto(transaction.nomenclature, transaction.storage, transaction.range)
            row = rows[key]
            if filter.date_from is not None and period < filter.date_from:
                row.opening_balance += transaction.value
            elif transaction.value > 0:
                row.receipt += transaction.value
            else:
                row.expense -= transaction.value
        for row in rows.values():
            row.closing_balance = row.opening_balance + row.receipt - row.expense
        result = turnover_prototype(transactions)
        result._data = list(rows.values())
        return result
