from datetime import datetime

from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Logics.turnover_prototype import turnover_prototype
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.transaction_model import transaction_model
from Src.Models.warehouse_model import warehouse_model
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model


def _transaction(name, quantity, period, item, warehouse, unit=None):
    """Подготовить складскую операцию для проверки ведомости."""
    result = transaction_model(name)
    result.value = quantity
    result.period = period
    result.nomenclature = item
    result.storage = warehouse
    result.range = unit if unit is not None else item.range
    return result


def test_success_turnover_opening_movements_and_closing():
    """Начальный остаток учитывает все прошлые операции; обе границы периода включены."""
    # Подготовка
    item = nomenclature_model.create_flour()
    warehouse = warehouse_model.create_main()
    transactions = [
        _transaction("Начальное поступление", 10, "2026-10-30T00:00:00", item, warehouse),
        _transaction("Начальное списание", -2, "2026-10-31T00:00:00", item, warehouse),
        _transaction("Приход на границе", 5, "2026-11-01T00:00:00", item, warehouse),
        _transaction("Расход на границе", -3, "2026-11-30T23:00:00", item, warehouse),
        _transaction("Будущая операция", 100, "2026-12-01T00:00:00", item, warehouse),
    ]
    pr = turnover_prototype(transactions)
    filter = filter_dto.from_dict({"date_from": "2026-11-01T00:00:00Z", "date_to": "2026-11-30T23:00:00Z"})

    # Действие
    result = pr.clone(filter)
    row = result.data[0]

    # Проверки
    assert isinstance(result, turnover_prototype)
    assert len(result.data) == 1
    assert row.opening_balance == 8
    assert row.receipt == 5
    assert row.expense == 3
    assert row.closing_balance == 10
    assert row.nomenclature is item
    assert row.storage is warehouse
    assert pr.data == transactions
    assert transactions[-1].value == 100


def test_success_turnover_separates_warehouses_items_and_units():
    """Разные склады, номенклатуры и единицы образуют отдельные строки."""
    # Подготовка
    gram = range_model.create_gramm()
    kilogram = range_model("кг", 1000, gram)
    group = group_model.create_raw()
    flour = nomenclature_model("Мука", "Мука", group, kilogram)
    sugar = nomenclature_model("Сахар", "Сахар", group, kilogram)
    main = warehouse_model.create_main()
    kitchen = warehouse_model.create_kitchen()
    transactions = [
        _transaction("Мука на основном", 1, datetime(2026, 11, 1), flour, main),
        _transaction("Мука в граммах", 500, datetime(2026, 11, 1), flour, main, gram),
        _transaction("Мука на кухне", 2, datetime(2026, 11, 1), flour, kitchen),
        _transaction("Сахар на основном", 3, datetime(2026, 11, 1), sugar, main),
    ]

    # Действие
    rows = turnover_prototype(transactions).clone(filter_dto()).data

    # Проверки
    actual = {(row.storage.id, row.nomenclature.id, row.range.id): row.closing_balance for row in rows}
    assert actual == {
        (main.id, flour.id, kilogram.id): 1,
        (main.id, flour.id, gram.id): 500,
        (kitchen.id, flour.id, kilogram.id): 2,
        (main.id, sugar.id, kilogram.id): 3,
    }
    assert all(row.opening_balance == 0 for row in rows)


def test_success_turnover_filters_nested_nomenclature_before_aggregation():
    """Фильтр номенклатуры применяется и к начальному остатку, и к оборотам периода."""
    # Подготовка
    flour = nomenclature_model.create_flour()
    sugar = nomenclature_model.create_sugar()
    warehouse = warehouse_model.create_main()
    transactions = [
        _transaction("Приход муки до периода", 10, "2026-10-31T00:00:00", flour, warehouse),
        _transaction("Расход муки", -2, "2026-11-10T00:00:00", flour, warehouse),
        _transaction("Приход сахара", 100, "2026-11-10T00:00:00", sugar, warehouse),
    ]
    filter = filter_dto([filter_item_dto("id", "EQUALS", flour.id)], date_from="2026-11-01T00:00:00Z")

    # Действие
    rows = turnover_prototype(transactions).clone(filter).data

    # Проверки
    assert len(rows) == 1
    assert rows[0].nomenclature is flour
    assert rows[0].opening_balance == 10
    assert rows[0].expense == 2
    assert rows[0].closing_balance == 8


def test_success_turnover_missing_boundaries_and_empty_results():
    """Без начала все операции относятся к оборотам; будущие и ненайденные операции не создают строк."""
    # Подготовка
    item = nomenclature_model.create_flour()
    warehouse = warehouse_model.create_main()
    transactions = [_transaction("Операция", -5, "2026-11-10T00:00:00", item, warehouse)]
    pr = turnover_prototype(transactions)

    # Действие
    all_rows = pr.clone(filter_dto()).data
    future_only = pr.clone(filter_dto(date_to="2026-11-01T00:00:00Z")).data
    opening_only = pr.clone(filter_dto(date_from="2026-12-01T00:00:00Z")).data
    missing = pr.clone(filter_dto([filter_item_dto("name", "EQUALS", "Нет совпадений")])).data

    # Проверки
    assert all_rows[0].opening_balance == 0
    assert all_rows[0].expense == 5
    assert all_rows[0].closing_balance == -5
    assert future_only == []
    assert opening_only[0].opening_balance == -5
    assert opening_only[0].receipt == opening_only[0].expense == 0
    assert missing == []
    assert turnover_prototype([]).clone(filter_dto()).data == []


def test_success_turnover_normalizes_timezones():
    """Дата операции и границы с разными часовыми поясами сравниваются как UTC."""
    # Подготовка
    item = nomenclature_model.create_flour()
    warehouse = warehouse_model.create_main()
    transaction = _transaction("Операция", 5, "2026-11-01T08:00:00+08:00", item, warehouse)
    filter = filter_dto(date_from="2026-11-01T00:00:00Z", date_to="2026-11-01T00:00:00Z")

    # Действие
    rows = turnover_prototype([transaction]).clone(filter).data

    # Проверки
    assert rows[0].opening_balance == 0
    assert rows[0].receipt == 5


def test_success_turnover_can_clone_a_report_again():
    """Готовая ведомость клонируется по сохранённым операциям, а не по агрегированным строкам."""
    # Подготовка
    item = nomenclature_model.create_flour()
    warehouse = warehouse_model.create_main()
    transactions = [
        _transaction("Приход", 10, "2026-11-01T00:00:00", item, warehouse),
        _transaction("Расход", -3, "2026-11-20T00:00:00", item, warehouse),
    ]
    original = turnover_prototype(transactions).clone(filter_dto())

    # Действие
    result = original.clone(filter_dto(date_to="2026-11-10T00:00:00Z"))

    # Проверки
    assert original.data[0].closing_balance == 7
    assert result.data[0].closing_balance == 10
    assert result.data[0] is not original.data[0]
