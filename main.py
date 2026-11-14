import connexion
from connexion.resolver import RelativeResolver
from flask import Response, jsonify, redirect
from Src.Core.exception import arguments_exception, entity_conflict_exception, entity_not_found_exception
from Src.Logics.entity_controller import entity_controller
from Src.Logics.entity_service import entity_service
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum

app = connexion.FlaskApp(__name__)

settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()
service = entity_service(storage)
controller = entity_controller(service)

factory = report_factory(settings.settings)
report = factory.create(report_type_enum.TXT)


@app.route("/")
@app.route("/docs")
def swagger_ui_redirect():
    """Открыть встроенный интерфейс Swagger UI."""
    return redirect("/ui/")


@app.app.errorhandler(arguments_exception)
def invalid_arguments(error):
    """Вернуть ошибку аргументов приложения в формате JSON."""
    return jsonify(detail=str(error)), 400


@app.app.errorhandler(entity_conflict_exception)
def entity_conflict(error):
    """Вернуть конфликт уникальности или входящих ссылок."""
    return jsonify(detail=error.message), 409


@app.app.errorhandler(entity_not_found_exception)
def entity_not_found(error):
    """Вернуть отсутствие типа или кода сущности."""
    return jsonify(detail=error.message), 404


def get_entities():
    """Получить типы сущностей, поддерживаемых хранилищем."""
    return jsonify(service.entity_types)


def get_report_formats():
    """Получить форматы, зарегистрированные в фабрике отчётов."""
    return jsonify(factory.formats)


def get_default_report(entity: str, unique_code: str):
    """Получить отчёт по умолчанию; параметры проверяет и передаёт Connexion."""
    return get_entity_report_default(entity, unique_code)


def get_report():
    """Получить текстовый отчёт по первому рецепту."""
    recipe = storage.recipes[0]
    result = report.build(recipe)
    return Response(result.text, mimetype="text/plain; charset=utf-8")


def get_entity_report(format_name: str, entity_type: str, entity_id: str):
    """
    Метод GET формирует отчет в указанном формате и для указанного типа и кода сущности.
    """
    try:
        fmt_str = format_name.strip().upper()
        if fmt_str == "MD":
            fmt_str = "MARKDOWN"
        fmt_enum = report_type_enum[fmt_str]
    except KeyError:
        return Response(f"Неизвестный формат: {format_name}", status=400, mimetype="text/plain; charset=utf-8")

    entity = service.get_by_type_and_id(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create(fmt_enum)
    result = rep.build(entity)
    return rep.create_response(result, f"{entity_type}_{entity_id}")


def get_entity_report_default(entity_type: str, entity_id: str):
    """
    Метод GET формирует данные для указанного типа и кода сущности с использованием create_default.
    """
    entity = service.get_by_type_and_id(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create_default()
    result = rep.build(entity)
    return rep.create_response(result, f"{entity_type}_{entity_id}_default")


app.add_api(
    "openapi.yaml",
    resolver=RelativeResolver(__name__),
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8089)
