import pytest
from main import app
from Src.Logics.storage_manager import storage_manager
from Src.Dtos.report_type_enum import report_type_enum


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_api_get_report_legacy(client):
    """
    Проверка базового эндпоинта получения отчета рецепта в формате TXT.
    """
    # Подготовка и действие
    response = client.get("/api/get_report")

    # Проверка
    assert response.status_code == 200
    assert "Код | Наименование | Брутто | Нетто" in response.get_data(as_text=True)


def test_api_get_entity_report_markdown(client):
    """
    Проверка эндпоинта получения Markdown-отчета (бинарные данные и скачивание файла).
    """
    # Подготовка
    sm = storage_manager()
    recipe = sm.recipes[0]

    # Действие
    response = client.get(f"/api/report/markdown/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert response.mimetype == "text/markdown"
    assert f'attachment; filename="recipe_{recipe.id}.md"' in response.headers.get("Content-Disposition", "")
    content = response.data.decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in content
    assert recipe.rows[0].nomenclature.name in content


def test_api_get_entity_report_csv(client):
    """
    Проверка эндпоинта получения CSV-отчета (бинарные данные и скачивание файла).
    """
    # Подготовка
    sm = storage_manager()
    nomenclature = sm.nomenclatures[0]

    # Действие
    response = client.get(f"/api/report/csv/nomenclature/{nomenclature.id}")

    # Проверка
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert f'attachment; filename="nomenclature_{nomenclature.id}.csv"' in response.headers.get("Content-Disposition", "")
    content = response.data.decode("utf-8")
    assert "Код;Краткое наименование;Полное наименование;Группа;Единица измерения" in content
    assert nomenclature.name in content


def test_api_get_entity_report_xml(client):
    """
    Проверка эндпоинта получения XML-отчета как структурированного текста.
    """
    # Подготовка
    sm = storage_manager()
    range_item = sm.ranges[0]

    # Действие
    response = client.get(f"/api/report/xml/range/{range_item.id}")

    # Проверка
    assert response.status_code == 200
    assert response.mimetype == "application/xml"
    content = response.get_data(as_text=True)
    assert "<range>" in content
    assert range_item.name in content


def test_api_get_entity_report_default(client):
    """
    Проверка эндпоинта получения отчета по умолчанию (create_default).
    """
    # Подготовка
    sm = storage_manager()
    recipe = sm.recipes[0]

    # Действие
    response = client.get(f"/api/report/default/recipe/{recipe.id}")

    # Проверка
    assert response.status_code == 200
    assert response.mimetype == "text/markdown"
    assert f'attachment; filename="recipe_{recipe.id}_default.md"' in response.headers.get("Content-Disposition", "")
    content = response.data.decode("utf-8")
    assert "| Код | Наименование | Брутто | Нетто |" in content


def test_api_get_entity_report_not_found(client):
    """
    Проверка возврата ошибки 404 при отсутствии сущности.
    """
    # Подготовка и действие
    response = client.get("/api/report/xml/recipe/non_existent_id")

    # Проверка
    assert response.status_code == 404


def test_api_get_entity_report_txt_nomenclature(client):
    """
    Проверка эндпоинта получения отчета по номенклатуре в формате TXT.
    """
    # Подготовка
    sm = storage_manager()
    nomenclature = sm.nomenclatures[0]

    # Действие
    response = client.get(f"/api/report/txt/nomenclature/{nomenclature.id}")

    # Проверка
    assert response.status_code == 200
    assert response.mimetype == "text/plain"
    content = response.get_data(as_text=True)
    assert "Краткое наименование" in content
    assert nomenclature.name in content

