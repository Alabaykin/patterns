import importlib
from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto


class text_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате TXT.
    Определяет метаданные формата и делегирует формирование конкретного отчета фабрике.
    """

    @property
    def mimetype(self) -> str:
        """
        MIME-тип контента отчёта в текстовом формате.
        """
        return "text/plain; charset=utf-8"

    @property
    def is_attachment(self) -> bool:
        """
        Флаг отправки отчета в качестве скачиваемого вложения.
        """
        return False

    @property
    def file_extension(self) -> str:
        """
        Расширение файла для формата отчёта.
        """
        return "txt"

    def build(self, source: abstract_entity) -> report_result_dto:
        """
        Сформировать отчёт для переданной сущности через фабрику отчетов.
        """
        from Src.Logics.report_factory import report_factory
        from Src.Dtos.report_type_enum import report_type_enum
        reporter = report_factory().create(report_type_enum.TXT, source)
        return reporter.build(source)


def __getattr__(name: str):
    """
    Ленивый импорт специализированных классов текстовых отчётов для обратной совместимости.
    """
    if name in ("recipe_text_report", "nomenclature_text_report", "range_text_report"):
        mod = importlib.import_module(f"Src.Logics.Reports.Text.{name}")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")