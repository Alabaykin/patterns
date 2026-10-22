from Src.Core.abstract_report import abstract_report


class csv_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате CSV.
    Определяет метаданные формата (MIME-тип, расширение, режим вложения).
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        """
        MIME-тип контента отчёта в формате CSV.
        """
        return "text/csv"

    @property
    def is_attachment(self) -> bool:
        """
        Флаг формирования отчета как вложения (скачиваемый файл).
        """
        return True

    @property
    def file_extension(self) -> str:
        """
        Расширение файла отчета.
        """
        return "csv"

    def _resolve_handler(self, source):
        """
        Поиск специализированного обработчика по типу доменной модели.
        """
        if type(self) is not csv_report:
            return self
        handler_cls = self._handlers.get(type(source))
        if handler_cls:
            return handler_cls()
        return self


def _init_handlers():
    from Src.Models.recipe_model import recipe_model
    from Src.Models.nomenclature_model import nomenclature_model
    from Src.Models.range_model import range_model
    from Src.Logics.Reports.Csv.recipe_csv_report import recipe_csv_report
    from Src.Logics.Reports.Csv.nomenclature_csv_report import nomenclature_csv_report
    from Src.Logics.Reports.Csv.range_csv_report import range_csv_report

    csv_report._handlers = {
        recipe_model: recipe_csv_report,
        nomenclature_model: nomenclature_csv_report,
        range_model: range_csv_report,
    }


_init_handlers()


def __getattr__(name: str):
    """
    Ленивый импорт специализированных отчетов для обратной совместимости.
    """
    if name in ("recipe_csv_report", "nomenclature_csv_report", "range_csv_report"):
        import importlib
        mod = importlib.import_module(f"Src.Logics.Reports.Csv.{name}")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

