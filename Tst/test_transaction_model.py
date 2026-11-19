import pytest
from datetime import datetime

from Src.Core.exception import arguments_exception, entity_conflict_exception
from Src.Logics.storage_manager import storage_manager
from Src.Logics.entity_service import entity_service
from Src.Models.transaction_model import transaction_model


def test_success_transaction_value():
    """Положительное поступление и отрицательное списание сохраняются в модели."""
    # Подготовка
    transaction = transaction_model()

    # Действие
    transaction.value = 10.0
    receipt = transaction.value
    transaction.value = -5.0

    # Проверки
    assert receipt == 10.0
    assert transaction.value == -5.0


def test_raise_transaction_zero_value():
    """Нулевое количество отклоняется без изменения предыдущего значения."""
    # Подготовка
    transaction = transaction_model()
    transaction.value = 10.0

    # Действие и проверки
    with pytest.raises(arguments_exception):
        transaction.value = 0
    assert transaction.value == 10.0


def test_success_storage_transaction_links_after_reload(tmp_path):
    """Транзакция сохраняет дату и общие ссылки после выгрузки и загрузки хранилища."""
    # Подготовка
    storage = storage_manager()
    storage.load()
    source = storage.transactions[0]
    path = tmp_path / "transactions.json"

    # Действие
    storage.save(str(path))
    storage.load(str(path))
    restored = storage.transactions[0]

    # Проверки
    assert restored is not source
    assert restored.id == source.id
    assert restored.value == 10
    assert restored.period == datetime(2026, 11, 11)
    assert restored.range is storage.find(restored.range.id)
    assert restored.storage is storage.find(restored.storage.id)
    assert restored.nomenclature is storage.find(restored.nomenclature.id)


def test_raise_delete_warehouse_used_by_transaction():
    """Склад нельзя удалить или перекодировать до удаления использующей его транзакции."""
    # Подготовка
    storage = storage_manager()
    storage.load()
    service = entity_service(storage)
    transaction = storage.transactions[0]
    warehouse = transaction.storage

    try:
        # Действие и проверки
        with pytest.raises(entity_conflict_exception):
            service.delete("warehouse", warehouse.id)
        with pytest.raises(entity_conflict_exception):
            service.update("warehouse", warehouse.id, {"id": "new-warehouse-code", "name": warehouse.name})
        service.delete("transaction", transaction.id)
        service.delete("warehouse", warehouse.id)
        assert storage.find(warehouse.id) is None
    finally:
        storage.load()
