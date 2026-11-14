from main import app, factory, storage
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.report_type_enum import report_type_enum


def test_api_get_report_legacy():
    """
    Проверка базового эндпоинта получения отчета рецепта в формате TXT.
    """
    with app.test_client() as client:
        # Подготовка и действие
        response = client.get("/api/get_report")

        # Проверка
        assert response.status_code == 200
        assert "gross" in response.text and "net" in response.text


def test_api_get_entity_report_markdown():
    """
    Проверка эндпоинта получения Markdown-отчета (бинарные данные и скачивание файла).
    """
    with app.test_client() as client:
        # Подготовка
        sm = storage_manager()
        recipe = sm.recipes[0]

        # Действие
        response = client.get(f"/api/report/markdown/recipe/{recipe.id}")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].split(";")[0] == "text/markdown"
        assert f'attachment; filename="recipe_{recipe.id}.md"' in response.headers.get("Content-Disposition", "")
        content = response.content.decode("utf-8")
        assert "gross" in content and "net" in content
        assert recipe.rows[0].nomenclature.name in content


def test_api_get_entity_report_csv():
    """
    Проверка эндпоинта получения CSV-отчета (бинарные данные и скачивание файла).
    """
    with app.test_client() as client:
        # Подготовка
        sm = storage_manager()
        nomenclature = sm.nomenclatures[0]

        # Действие
        response = client.get(f"/api/report/csv/nomenclature/{nomenclature.id}")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].split(";")[0] == "text/csv"
        assert f'attachment; filename="nomenclature_{nomenclature.id}.csv"' in response.headers.get("Content-Disposition", "")
        content = response.content.decode("utf-8")
        assert content.startswith("section;row;field;value")
        assert nomenclature.name in content


def test_api_get_entity_report_xml():
    """
    Проверка эндпоинта получения XML-отчета как структурированного текста.
    """
    with app.test_client() as client:
        # Подготовка
        sm = storage_manager()
        range_item = sm.ranges[0]

        # Действие
        response = client.get(f"/api/report/xml/range/{range_item.id}")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].split(";")[0] == "application/xml"
        content = response.text
        assert '<report title="range_model">' in content
        assert range_item.name in content


def test_api_get_entity_report_default():
    """
    Проверка эндпоинта получения отчета по умолчанию (create_default).
    """
    with app.test_client() as client:
        # Подготовка
        sm = storage_manager()
        recipe = sm.recipes[0]

        # Действие
        response = client.get(f"/api/report/default/recipe/{recipe.id}")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].split(";")[0] == "text/markdown"
        assert f'attachment; filename="recipe_{recipe.id}_default.md"' in response.headers.get("Content-Disposition", "")
        content = response.content.decode("utf-8")
        assert "gross" in content and "net" in content


def test_api_get_entity_report_not_found():
    """
    Проверка возврата ошибки 404 при отсутствии сущности.
    """
    with app.test_client() as client:
        # Подготовка и действие
        response = client.get("/api/report/xml/recipe/non_existent_id")

        # Проверка
        assert response.status_code == 404


def test_api_get_entity_report_txt_nomenclature():
    """
    Проверка эндпоинта получения отчета по номенклатуре в формате TXT.
    """
    with app.test_client() as client:
        # Подготовка
        sm = storage_manager()
        nomenclature = sm.nomenclatures[0]

        # Действие
        response = client.get(f"/api/report/txt/nomenclature/{nomenclature.id}")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].split(";")[0] == "text/plain"
        content = response.text
        assert "full_name:" in content
        assert nomenclature.name in content


def test_success_get_entities_returns_storage_types():
    """
    Список типов из YAML-маршрута совпадает с типами хранилища.
    """
    with app.test_client() as client:
        # Подготовка
        expected = storage.entity_types

        # Действие
        response = client.get("/api/get_entities")

        # Проверка
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        assert response.json() == expected


def test_success_default_report_preserves_format():
    """
    YAML-маршрут использует фабрику и сохраняет формат и способ выдачи отчёта.
    """
    for entity_type in ["range_model", "nomenclature_model", "recipe_model", "group_model", "warehouse_model"]:
        for format_type, mimetype in [
            (report_type_enum.TXT, "text/plain"),
            (report_type_enum.MARKDOWN, "text/markdown"),
            (report_type_enum.CSV, "text/csv"),
            (report_type_enum.XML, "application/xml"),
            (report_type_enum.HTML, "text/html"),
        ]:
            with app.test_client() as client:
                # Подготовка
                original_format = factory.settings.response_format
                factory.settings.response_format = format_type
                try:
                    item = storage.get_by_type_and_id(entity_type, {
                        "range_model": "кг", "nomenclature_model": "Мука пшеничная", "recipe_model": "Песочное тесто",
                        "group_model": "Сырье", "warehouse_model": "Основной склад",
                    }[entity_type])
                    generator = factory.create_default()
                    expected = generator.build(item)

                    # Действие
                    response = client.get("/api/get_default_report", params={"entity": entity_type, "unique_code": item.id})

                    # Проверка
                    assert response.status_code == 200
                    assert response.headers["content-type"].split(";")[0] == mimetype
                    assert response.content == (bytes(expected.binary) if generator.is_attachment else expected.text.encode("utf-8"))
                    assert ("Content-Disposition" in response.headers) == generator.is_attachment
                finally:
                    factory.settings.response_format = original_format


def test_bad_request_default_report_parameters_validated_by_yaml():
    """
    Connexion отклоняет отсутствующие и пустые параметры по правилам YAML.
    """
    for params in [
        {},
        {"entity": "range_model"},
        {"unique_code": "кг"},
        {"entity": "range_model", "unique_code": ""},
        {"entity": " ", "unique_code": "кг"},
    ]:
        with app.test_client() as client:
            # Подготовка
            url = "/api/get_default_report"

            # Действие
            response = client.get(url, params=params)

            # Проверка
            assert response.status_code == 400
            assert response.json()["detail"]


def test_not_found_default_report_unknown_id():
    """
    Несуществующий объект приводит к 404.
    """
    with app.test_client() as client:
        # Подготовка
        params = {"entity": "range_model", "unique_code": "missing"}

        # Действие
        response = client.get("/api/get_default_report", params=params)

        # Проверка
        assert response.status_code == 404


def test_not_found_default_report_unknown_entity_type():
    """
    Неизвестный тип отклоняется при поиске сущности в хранилище.
    """
    with app.test_client() as client:
        # Подготовка
        entity_type = "missing_model"

        # Действие
        response = client.get("/api/get_default_report", params={"entity": entity_type, "unique_code": "missing"})

        # Проверка
        assert response.status_code == 404


def test_success_default_report_lookup_by_name():
    """
    Пример из Swagger работает с точным наименованием единицы измерения.
    """
    with app.test_client() as client:
        # Подготовка
        params = {"entity": "range_model", "unique_code": "кг"}

        # Действие
        response = client.get("/api/get_default_report", params=params)

        # Проверка
        assert response.status_code == 200
        assert "кг" in response.text
