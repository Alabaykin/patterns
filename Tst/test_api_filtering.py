from main import app, storage, service
from Src.Logics.convert_factory import convert_factory


def test_success_api_filters_all_domain_types_without_changes():
    """POST фильтрует четыре справочника одним DTO и не изменяет хранилище."""
    # Подготовка
    storage.load()
    serializer = convert_factory()
    before = serializer.serialize(storage.data)
    cases = {
        "group_model": storage.groups[0],
        "range_model": storage.ranges[0],
        "nomenclature_model": storage.nomenclatures[0],
        "recipe_model": storage.recipes[0],
    }

    with app.test_client() as client:
        for entity_type, item in cases.items():
            # Действие
            response = client.post(f"/api/filter/{entity_type}", json={
                "filters": [{"field_name": "id", "filter_type": "EQUALS", "value": item.id}],
                "recursive": False,
            })
            by_name = client.post(f"/api/filter/{entity_type}", json={
                "filters": [{"field_name": "name", "filter_type": "LIKE", "value": item.name}],
                "recursive": False,
            })

            # Проверки
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("application/json")
            assert response.json() == [serializer.serialize(item)]
            assert by_name.status_code == 200
            assert item.id in [found["id"] for found in by_name.json()]
    assert serializer.serialize(storage.data) == before


def test_success_api_nested_filter_and_group_integrity():
    """Поиск находит базовую единицу и владельца группы, а CRUD сохраняет целостность иерархии."""
    # Подготовка
    storage.load()
    parent = service.create("group", {"name": "Владелец для фильтра"})
    child = service.create("group", {"name": "Дочерняя для фильтра", "parent": {"id": parent.id}})
    unit = next(item for item in storage.ranges if item.base_range is not None)

    try:
        with app.test_client() as client:
            # Действие
            groups = client.post("/api/filter/group_model", json={
                "filters": [{"field_name": "id", "value": parent.id}],
            })
            units = client.post("/api/filter/range_model", json={
                "filters": [{"field_name": "id", "value": unit.base_range.id}],
            })
            blocked = client.delete(f"/api/entities/group_model/{parent.id}")
            cycle = client.put(f"/api/entities/group_model/{parent.id}", json={
                "name": parent.name, "parent": {"id": child.id},
            })

            # Проверки
            assert groups.status_code == 200
            assert {parent.id, child.id} <= {item["id"] for item in groups.json()}
            assert units.status_code == 200
            assert unit.id in [item["id"] for item in units.json()]
            assert blocked.status_code == 409
            assert cycle.status_code == 400
            assert parent.parent is None
    finally:
        storage.load()


def test_raise_api_invalid_filters_and_unknown_type():
    """Неверные DTO возвращают 400, неизвестный тип — 404; пустой результат — 200."""
    # Подготовка
    storage.load()
    before = convert_factory().serialize(storage.data)
    cases = [
        {"filters": [{"field_name": "name", "filter_type": "unknown", "value": "Мука"}]},
        {"filters": [{"field_name": "__dict__", "value": "Мука"}]},
        {"filters": [{"field_name": "name", "value": 1}]},
        {"filters": [{"field_name": "name", "value": ""}]},
        {"filters": "name"}, {"recursive": "yes"}, {"extra": 1},
        {"date_from": "2026-12-01T00:00:00Z", "date_to": "2026-11-01T00:00:00Z"},
    ]

    with app.test_client() as client:
        for body in cases:
            # Действие и проверки
            assert client.post("/api/filter/group_model", json=body).status_code == 400
            assert client.post("/api/turnover", json=body).status_code == 400
        assert client.post("/api/filter/group_model", json=[]).status_code == 400
        assert client.post("/api/filter/group_model").status_code == 400
        assert client.post("/api/filter/unknown_model", json={}).status_code == 404
        assert client.post("/api/filter/group_model", json={"date_from": "2026-11-01T00:00:00Z"}).status_code == 400
        missing = client.post("/api/filter/group_model", json={
            "filters": [{"field_name": "name", "value": "Такой группы точно нет"}],
        })
        assert missing.status_code == 200
        assert missing.json() == []
    assert convert_factory().serialize(storage.data) == before


def test_success_api_turnover_with_period_and_nested_filter():
    """ОСВ через HTTP учитывает начальный остаток, движения периода и вложенный фильтр товара."""
    # Подготовка
    storage.load()
    item = service.create("nomenclature", {
        "name": "Тестовая мука ОСВ", "full_name": "Тестовая мука ОСВ",
        "group": {"id": storage.groups[0].id}, "range": {"id": storage.ranges[0].id},
    })
    warehouse = storage.warehouses[0]
    for number, (quantity, period) in enumerate([
        (10, "2026-10-31T00:00:00"), (5, "2026-11-01T00:00:00"),
        (-3, "2026-11-30T23:00:00"), (100, "2026-12-01T00:00:00"),
    ]):
        service.create("transaction", {
            "name": f"Тестовое движение ОСВ {number}", "value": quantity, "period": period,
            "nomenclature": {"id": item.id}, "storage": {"id": warehouse.id}, "range": {"id": item.range.id},
        })
    before = convert_factory().serialize(storage.data)

    try:
        with app.test_client() as client:
            # Действие
            response = client.post("/api/turnover", json={
                "filters": [{"field_name": "name", "filter_type": "EQUALS", "value": item.name}],
                "date_from": "2026-11-01T00:00:00Z", "date_to": "2026-11-30T23:00:00Z",
            })

            # Проверки
            assert response.status_code == 200
            rows = response.json()
            assert len(rows) == 1
            assert rows[0]["nomenclature"]["id"] == item.id
            assert rows[0]["storage"]["id"] == warehouse.id
            assert rows[0]["range"]["id"] == item.range.id
            assert rows[0]["opening_balance"] == 10
            assert rows[0]["receipt"] == 5
            assert rows[0]["expense"] == 3
            assert rows[0]["closing_balance"] == 12
        assert convert_factory().serialize(storage.data) == before
    finally:
        storage.load()


def test_raise_api_transaction_without_required_fields():
    """Неполная транзакция отклоняется до сохранения, чтобы ОСВ получала корректные операции."""
    # Подготовка
    storage.load()
    before = convert_factory().serialize(storage.data)

    with app.test_client() as client:
        # Действие
        response = client.post("/api/entities/transaction_model", json={"name": "Неполная операция"})

        # Проверки
        assert response.status_code == 400
    assert convert_factory().serialize(storage.data) == before
