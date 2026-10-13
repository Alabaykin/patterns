from flask import Flask, Response
from Src.Logics.settings_manager import settings_manager
from Src.Logics.storage_manager import storage_manager
from Src.Logics.report_factory import report_factory
from Src.Dtos.report_type_enum import report_type_enum

app = Flask(__name__)

settings = settings_manager()
settings.load()

storage = storage_manager()
storage.load()

factory = report_factory()
report = factory.create(report_type_enum.TXT)



@app.route("/api/get_report", methods=["GET"])
def get_report():
    recipe = storage.recipes[0]
    result = report.build(recipe)
    return Response(result.text, mimetype="text/plain; charset=utf-8")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
