from main import app
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

