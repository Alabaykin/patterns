from flask import Flask, Response, request, abort
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum

app = Flask(__name__)

settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()

factory = report_factory(settings.settings)
report = factory.create(report_type_enum.TXT)


def _find_entity(entity_type: str, entity_id: str):
    """
    Поиск сущности по типу и идентификатору или наименованию
    entity_type: 'nomenclature' / 'номенклатура', 'range' / 'единица измерения', 'recipe' / 'рецепт'
    """
    t = entity_type.strip().lower()
    items = []
    if t in ("номенклатура", "nomenclature"):
        items = storage.nomenclatures
    elif t in ("единица измерения", "единица_измерения", "range", "unit"):
        items = storage.ranges
    elif t in ("рецепт", "recipe"):
        items = storage.recipes
    else:
        return None

    for item in items:
        if str(item.id).lower() == entity_id.lower() or str(item.name).lower() == entity_id.lower():
            return item
    return None


def _create_response(result, format_enum: report_type_enum):
    """
    Формирование Flask Response в зависимости от типа формата.
    Для Markdown, CSV - бинарные данные и скачивание файла.
    Для остальных - текст.
    """
    if format_enum in (report_type_enum.MARKDOWN, report_type_enum.CSV):
        # Бинарные данные
        if result.binary:
            binary_bytes = bytes(result.binary)
        else:
            binary_bytes = result.text.encode("utf-8")

        if format_enum == report_type_enum.CSV:
            mimetype = "text/csv"
            filename = "report.csv"
        else:
            mimetype = "text/markdown"
            filename = "report.md"

        return Response(
            binary_bytes,
            mimetype=mimetype,
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\""
            }
        )
    elif format_enum == report_type_enum.XML:
        return Response(result.text, mimetype="application/xml; charset=utf-8")
    elif format_enum == report_type_enum.HTML:
        return Response(result.text, mimetype="text/html; charset=utf-8")
    else:
        return Response(result.text, mimetype="text/plain; charset=utf-8")


@app.route("/api/get_report", methods=["GET"])
def get_report():
    recipe = storage.recipes[0]
    result = report.build(recipe)
    return Response(result.text, mimetype="text/plain; charset=utf-8")


@app.route("/api/report/<string:format_name>/<string:entity_type>/<string:entity_id>", methods=["GET"])
def get_entity_report(format_name: str, entity_type: str, entity_id: str):
    """
    Метод GET формирует отчет в указанном формате и для указанного типа и кода сущности.
    """
    fmt_enum = report_type_enum.from_string(format_name)
    if fmt_enum is None:
        return Response(f"Неизвестный формат: {format_name}", status=400, mimetype="text/plain; charset=utf-8")

    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create(fmt_enum)
    result = rep.build(entity)
    return _create_response(result, fmt_enum)


@app.route("/api/report/default/<string:entity_type>/<string:entity_id>", methods=["GET"])
def get_entity_report_default(entity_type: str, entity_id: str):
    """
    Метод GET формирует данные для указанного типа и кода сущности с использованием create_default.
    """
    entity = _find_entity(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create_default()
    result = rep.build(entity)

    default_format_name = settings.settings.response_format if settings.settings else "TXT"
    fmt_enum = report_type_enum.from_string(default_format_name) or report_type_enum.TXT
    return _create_response(result, fmt_enum)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
