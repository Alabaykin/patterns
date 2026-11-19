import pytest

from Src.Core.exception import arguments_exception
from Src.Dtos.filter_dto import filter_dto, filter_item_dto
from Src.Logics.prototype import prototype
from Src.Models.group_model import group_model
from Src.Logics.storage_manager import storage_manager
from Src.Models.settings_model import settings_model


def test_contains_data_prototype():
    """Клон содержит подходящие модели, не меняя исходный список и прототип."""
    # Подготовка
    raw = group_model.create_raw()
    dishes = group_model.create_dishes()
    source = [raw, dishes]
    pr = prototype(source)
    filter = filter_dto()
    item = filter_item_dto()
    item.field_name = "name"
    item.filter_type = "eq"
    item.value = raw.name
    filter.filters = [item]

    # Действие
    result = pr.clone(filter)
    assert len(result.data) == 1
    assert result.data[0] is raw
    result.data.clear()

    # Проверки
    assert result is not pr
    assert result.data == []
    assert pr.data == [raw, dishes]
    assert source == [raw, dishes]


def test_clone_prototype_applies_all_filters():
    """Все условия применяются совместно, модели остаются исходными объектами."""
    # Подготовка
    raw = group_model.create_raw()
    dishes = group_model.create_dishes()
    pr = prototype([raw, dishes])
    filter = filter_dto([
        filter_item_dto("name", "eq", raw.name),
        filter_item_dto("id", "eq", raw.id),
    ])

    # Действие
    result = pr.clone(filter)
    empty = pr.clone(filter_dto([filter_item_dto("name", "eq", "Неизвестная группа")]))
    unfiltered = pr.clone(filter_dto())

    # Проверки
    assert len(result.data) == 1
    assert result.data[0] is raw
    assert empty.data == []
    assert unfiltered.data == pr.data
    assert unfiltered.data is not pr.data


def test_clone_prototype_rejects_unknown_filter_type():
    """Неподдерживаемое условие отклоняется без изменения исходного прототипа."""
    # Подготовка
    raw = group_model.create_raw()
    pr = prototype([raw])
    filter = filter_dto([filter_item_dto("name", "unknown", raw.name)])

    # Действие и проверки
    with pytest.raises(arguments_exception):
        pr.clone(filter)
    assert pr.data == [raw]


def test_contains_storage_transactions_prototype():
    """Прототип фильтрует транзакции первого старта, как в примере очного занятия."""
    # Подготовка
    settings = settings_model()
    settings.is_first = True
    manager = storage_manager()
    manager.convert(settings)
    filter = filter_dto()
    item = filter_item_dto()
    item.field_name = "name"
    item.filter_type = "eq"
    item.value = "Поступление яиц"
    filter.filters = [item]
    pr = prototype(manager.data["transactions"])

    # Действие
    result = pr.clone(filter)

    # Проверки
    assert len(result.data) == 1
    assert result.data[0] is manager.transactions[0]
    assert result.data[0].value == 10
    assert result.data is not pr.data
