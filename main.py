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
    try:
        fmt_str = format_name.strip().upper()
        if fmt_str == "MD":
            fmt_str = "MARKDOWN"
        fmt_enum = report_type_enum[fmt_str]
    except KeyError:
        return Response(f"Неизвестный формат: {format_name}", status=400, mimetype="text/plain; charset=utf-8")

    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create(fmt_enum, entity_type)
    result = rep.build(entity)
    return rep.create_response(result, f"{entity_type}_{entity_id}")


@app.route("/api/report/default/<string:entity_type>/<string:entity_id>", methods=["GET"])
def get_entity_report_default(entity_type: str, entity_id: str):
    """
    Метод GET формирует данные для указанного типа и кода сущности с использованием create_default.
    """
    entity = storage.get_by_type_and_id(entity_type, entity_id)
    if entity is None:
        return Response(f"Сущность типа '{entity_type}' с id '{entity_id}' не найдена", status=404, mimetype="text/plain; charset=utf-8")

    rep = factory.create_default(entity_type)
    result = rep.build(entity)
    return rep.create_response(result, f"{entity_type}_{entity_id}_default")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8070)
