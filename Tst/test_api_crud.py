from main import app, storage, service
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.convert_factory import convert_factory


def _snapshot():
    """Полная копия данных для проверки отсутствия частичного изменения при ошибке."""
    return convert_factory().serialize(storage.data)


def _row(nomenclature, unit, sub_recipe=None):
    """Создать JSON строки рецепта со ссылками на существующие справочники."""
    result = {
        "type": "Src.Models.recipe_row_model.recipe_row_model",
        "nomenclature": {"id": nomenclature.id}, "range": {"id": unit.id},
        "gross": 1.0, "net": 0.9,
    }
    if sub_recipe is not None:
        result["sub_recipe"] = {"id": sub_recipe}
    return result


def test_success_api_get_report_formats():
    """
    Метод возвращает все форматы фабрики в JSON.
    """
    # Подготовка
    with app.test_client() as client:
        # Действие
        response = client.get("/api/get_report_formats")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert set(response.json()) == {item.name.lower() for item in report_type_enum}


def test_success_api_crud_all_entity_types():
    """
    Создание, список, чтение, изменение и удаление выполняются для всех пяти типов.
    """
    # Подготовка
    storage.load()
    cases = {
        "group_model": {"name": "Тестовая группа CRUD"},
        "warehouse_model": {"name": "Тестовый склад CRUD"},
        "range_model": {"name": "Тестовая единица CRUD", "coefficient": 2.0},
        "nomenclature_model": {
            "name": "Тестовая номенклатура CRUD", "full_name": "Полное имя",
            "group": {"id": storage.groups[0].id}, "range": {"id": storage.ranges[0].id},
        },
        "recipe_model": {"name": "Тестовый рецепт CRUD", "rows": [_row(storage.nomenclatures[0], storage.ranges[0])]},
    }
    try:
        with app.test_client() as client:
            for entity_type, payload in cases.items():
                url = f"/api/entities/{entity_type}"

                # Действие
                created = client.post(url, json=payload)

                # Проверка
                assert created.status_code == 201
                item = created.json()
                item_url = f"{url}/{item['id']}"
                assert created.headers["Location"] == item_url
                assert client.get(item_url).json() == item
                assert item in client.get(url).json()

                # Действие
                item["name"] += " изменён"
                updated = client.put(item_url, json=item)

                # Проверка
                assert updated.status_code == 200
                assert updated.json()["id"] == item["id"]
                assert client.get(item_url).json()["name"] == item["name"]

                # Действие
                deleted = client.delete(item_url)

                # Проверка
                assert deleted.status_code == 204
                assert deleted.content == b""
                assert client.get(item_url).status_code == 404
    finally:
        storage.load()


def test_conflict_api_group_links_and_success_after_removing_reference():
    """
    Группу нельзя удалить или перекодировать при использовании; переименование видно номенклатуре.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            group = client.post("/api/entities/group_model", json={"name": "Связанная группа"}).json()
            payload = {
                "name": "Связанный товар", "full_name": "Полное имя товара",
                "group": {"id": group["id"]}, "range": {"id": storage.ranges[0].id},
            }
            nomenclature = client.post("/api/entities/nomenclature_model", json=payload).json()
            url = f"/api/entities/group_model/{group['id']}"
            before = _snapshot()

            # Действие
            deleted = client.delete(url)
            recoded = client.put(url, json={"id": "new-group-code", "name": "Другое имя"})

            # Проверка
            assert deleted.status_code == 409
            assert nomenclature["name"] in deleted.json()["detail"]
            assert recoded.status_code == 409
            assert _snapshot() == before

            # Действие
            renamed = client.put(url, json={"name": "Новое имя группы"})
            related = client.get(f"/api/entities/nomenclature_model/{nomenclature['id']}")

            # Проверка
            assert renamed.status_code == 200
            assert renamed.json()["id"] == group["id"]
            assert related.json()["group"]["name"] == "Новое имя группы"
            assert service.get("nomenclature", nomenclature["id"]).group is service.get("group", group["id"])

            # Действие
            removed_usage = client.delete(f"/api/entities/nomenclature_model/{nomenclature['id']}")
            removed_group = client.delete(url)

            # Проверка
            assert removed_usage.status_code == 204
            assert removed_group.status_code == 204
    finally:
        storage.load()


def test_conflict_api_base_unit_used_by_derived_unit():
    """
    Базовая единица блокируется производной единицей даже без номенклатуры.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            base = client.post("/api/entities/range_model", json={"name": "Тестовая база"}).json()
            derived = client.post("/api/entities/range_model", json={
                "name": "Производная единица", "coefficient": 10, "base_range": {"id": base["id"]},
            }).json()
            url = f"/api/entities/range_model/{base['id']}"

            # Действие
            response = client.delete(url)

            # Проверка
            assert response.status_code == 409
            assert derived["name"] in response.json()["detail"]

            # Действие
            assert client.delete(f"/api/entities/range_model/{derived['id']}").status_code == 204
            response = client.delete(url)

            # Проверка
            assert response.status_code == 204
    finally:
        storage.load()


def test_conflict_api_nomenclature_used_in_recipe():
    """
    Начальные данные используют единые экземпляры и блокируют удаление ингредиента.
    """
    # Подготовка
    storage.load()
    ingredient = storage.nomenclatures[0]
    before = _snapshot()
    with app.test_client() as client:
        # Действие
        response = client.delete(f"/api/entities/nomenclature_model/{ingredient.id}")

        # Проверка
        assert response.status_code == 409
        assert _snapshot() == before


def test_conflict_api_nested_recipes_and_release_after_update():
    """
    Вложенные рецепты блокируются на любой глубине и освобождаются после снятия связи.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            leaf = client.post("/api/entities/recipe_model", json={"name": "Вложенный рецепт"}).json()
            middle = client.post("/api/entities/recipe_model", json={
                "name": "Промежуточный рецепт", "rows": [_row(storage.nomenclatures[0], storage.ranges[0], leaf["id"])],
            }).json()
            root = client.post("/api/entities/recipe_model", json={
                "name": "Главный рецепт", "rows": [_row(storage.nomenclatures[0], storage.ranges[0], middle["id"])],
            }).json()
            before = _snapshot()

            # Действие
            response = client.delete(f"/api/entities/recipe_model/{leaf['id']}")
            recoded = client.put(f"/api/entities/recipe_model/{leaf['id']}", json={"name": leaf["name"], "id": "other-code"})

            # Проверка
            assert response.status_code == 409
            assert middle["name"] in response.json()["detail"]
            assert root["name"] in response.json()["detail"]
            assert recoded.status_code == 409
            assert _snapshot() == before

            # Действие
            updated = client.put(f"/api/entities/recipe_model/{root['id']}", json={"name": root["name"], "rows": []})
            removed_middle = client.delete(f"/api/entities/recipe_model/{middle['id']}")
            removed_leaf = client.delete(f"/api/entities/recipe_model/{leaf['id']}")

            # Проверка
            assert updated.status_code == 200
            assert removed_middle.status_code == 204
            assert removed_leaf.status_code == 204
    finally:
        storage.load()


def test_success_api_change_free_entity_code():
    """
    У свободной сущности разрешена смена кода; прежний код больше не находится.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            item = client.post("/api/entities/warehouse_model", json={"name": "Свободный склад"}).json()
            old_url = f"/api/entities/warehouse_model/{item['id']}"

            # Действие
            response = client.put(old_url, json={"id": "new-warehouse-code", "name": "Перекодированный склад"})

            # Проверка
            assert response.status_code == 200
            assert client.get(old_url).status_code == 404
            assert client.get("/api/entities/warehouse_model/new-warehouse-code").json()["name"] == "Перекодированный склад"
    finally:
        storage.load()


def test_conflict_api_duplicate_codes_and_names_are_atomic():
    """
    Дубликаты имени и кода, в том числе кода другого типа, не перезаписывают записи.
    """
    # Подготовка
    storage.load()
    before = _snapshot()
    group = storage.groups[0]
    warehouse = storage.warehouses[0]
    with app.test_client() as client:
        # Действие
        duplicate_name = client.post("/api/entities/group_model", json={"name": group.name.upper()})
        duplicate_code = client.post("/api/entities/warehouse_model", json={"id": group.id, "name": "Новое имя"})
        update_duplicate = client.put(f"/api/entities/warehouse_model/{warehouse.id}", json={"id": group.id, "name": "Другое имя"})

        # Проверка
        assert duplicate_name.status_code == 409
        assert duplicate_code.status_code == 409
        assert update_duplicate.status_code == 409
        assert _snapshot() == before
        assert service.get("warehouse", warehouse.id) is warehouse


def test_bad_request_api_values_and_unknown_fields():
    """
    Некорректные значения, неизвестные поля и несовпадающий type отклоняются без записи.
    """
    # Подготовка
    storage.load()
    before = _snapshot()
    cases = [
        ("group_model", {"name": " "}),
        ("group_model", {"name": "Имя", "unknown": 1}),
        ("group_model", {"name": "Имя", "type": storage.warehouses[0].type}),
        ("group_model", {"name": "Имя", "id": "код/с-разделителем"}),
        ("range_model", {"name": "Единица", "coefficient": 0}),
        ("range_model", {"name": "Единица", "coefficient": True}),
        ("nomenclature_model", {"name": "Недостаточно полей"}),
        ("recipe_model", {"name": "Карта", "rows": "не список"}),
    ]
    with app.test_client() as client:
        for entity_type, payload in cases:
            # Действие
            response = client.post(f"/api/entities/{entity_type}", json=payload)

            # Проверка
            assert response.status_code == 400
            assert _snapshot() == before


def test_bad_request_api_invalid_and_changed_nested_references():
    """
    Нельзя создавать потерянные ссылки или менять справочник внутри другого запроса.
    """
    # Подготовка
    storage.load()
    group = storage.groups[0]
    before = _snapshot()
    modified_group = convert_factory().serialize(group)
    modified_group["name"] = "Скрытое изменение"
    orphan_group = {"id": "orphan", "name": "Отсутствующая группа", "type": group.type}
    with app.test_client() as client:
        for reference in [{"id": "missing"}, {"id": storage.warehouses[0].id}, modified_group, orphan_group]:
            payload = {"name": "Товар", "full_name": "Товар", "range": {"id": storage.ranges[0].id}, "group": reference}

            # Действие
            response = client.post("/api/entities/nomenclature_model", json=payload)

            # Проверка
            assert response.status_code == 400
            assert _snapshot() == before


def test_bad_request_api_update_cycle_and_invalid_late_field_are_atomic():
    """
    Самоссылка, цикл единиц и ошибка последнего поля сохраняют прежний граф и экземпляры.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            first = client.post("/api/entities/range_model", json={"name": "Единица A"}).json()
            second = client.post("/api/entities/range_model", json={"name": "Единица B", "base_range": {"id": first["id"]}}).json()
            before = _snapshot()
            original = service.get("range", first["id"])

            for reference in [first["id"], second["id"]]:
                # Действие
                response = client.put(f"/api/entities/range_model/{first['id']}", json={
                    "name": "Изменённое имя", "base_range": {"id": reference},
                })

                # Проверка
                assert response.status_code == 400
                assert _snapshot() == before
                assert service.get("range", first["id"]) is original

            # Действие
            response = client.put(f"/api/entities/range_model/{first['id']}", json={"name": "Другое имя", "coefficient": -1})

            # Проверка
            assert response.status_code == 400
            assert _snapshot() == before
    finally:
        storage.load()


def test_not_found_api_unknown_entity_and_code():
    """
    Неизвестные типы, отсутствующие коды и поиск по имени вместо кода возвращают 404.
    """
    # Подготовка
    storage.load()
    with app.test_client() as client:
        # Действие
        responses = [
            client.get("/api/entities/unknown"),
            client.get("/api/entities/group_model/missing"),
            client.get(f"/api/entities/group_model/{storage.warehouses[0].id}"),
            client.get(f"/api/entities/group_model/{storage.groups[0].name}"),
            client.delete("/api/entities/group_model/missing"),
            client.put("/api/entities/group_model/missing", json={"name": "Имя"}),
        ]

        # Проверка
        assert all(response.status_code == 404 for response in responses)


def test_bad_request_api_late_recipe_row_error_preserves_existing_graph():
    """
    Ошибка в новой строке не меняет прежние строки рецепта и связанные справочники.
    """
    # Подготовка
    storage.load()
    recipe = storage.recipes[0]
    before = _snapshot()
    payload = convert_factory().serialize(recipe)
    payload["name"] = "Не должно примениться"
    payload["rows"][-1]["net"] = payload["rows"][-1]["gross"] + 1

    with app.test_client() as client:
        # Действие
        response = client.put(f"/api/entities/recipe_model/{recipe.id}", json=payload)

        # Проверка
        assert response.status_code == 400
        assert service.get("recipe", recipe.id) is recipe
        assert _snapshot() == before


def test_bad_request_api_missing_or_invalid_json_body():
    """
    Отсутствующее, повреждённое или не являющееся объектом JSON-тело не меняет данные.
    """
    # Подготовка
    storage.load()
    before = _snapshot()
    with app.test_client() as client:
        # Действие
        responses = [
            client.post("/api/entities/group_model"),
            client.post("/api/entities/group_model", json=[]),
            client.post("/api/entities/group_model", content="{broken", headers={"Content-Type": "application/json"}),
        ]

        # Проверка
        assert all(response.status_code == 400 for response in responses)
        assert _snapshot() == before


def test_success_api_non_ascii_code_location_is_usable():
    """
    Явно заданный русский код возвращается в корректном Location и доступен для GET.
    """
    # Подготовка
    storage.load()
    try:
        with app.test_client() as client:
            # Действие
            created = client.post("/api/entities/group_model", json={"id": "группа-новая", "name": "Русский код"})
            response = client.get(created.headers["Location"])

            # Проверка
            assert created.status_code == 201
            assert response.status_code == 200
            assert response.json()["id"] == "группа-новая"
    finally:
        storage.load()
