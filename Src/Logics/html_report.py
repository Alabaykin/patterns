from Src.Core.abstract_report import abstract_report


class html_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате HTML.
    Определяет метаданные формата (MIME-тип, расширение, режим вложения).
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        """
        MIME-тип контента отчёта в формате HTML.
        """
        return "text/html"

    @property
    def is_attachment(self) -> bool:
        """
        Флаг формирования отчета как вложения.
        """
        return False

    @property
    def file_extension(self) -> str:
        """
        Расширение файла отчета.
        """
        return "html"

    def _resolve_handler(self, source):
        """
        Поиск специализированного обработчика по типу доменной модели.
        """
        if type(self) is not html_report:
            return self
        handler_cls = self._handlers.get(type(source))
        if handler_cls:
            return handler_cls()
        return self


def _init_handlers():
    from Src.Models.recipe_model import recipe_model
    from Src.Models.nomenclature_model import nomenclature_model
    from Src.Models.range_model import range_model
    from Src.Logics.Reports.Html.recipe_html_report import recipe_html_report
    from Src.Logics.Reports.Html.nomenclature_html_report import nomenclature_html_report
    from Src.Logics.Reports.Html.range_html_report import range_html_report

    html_report._handlers = {
        recipe_model: recipe_html_report,
        nomenclature_model: nomenclature_html_report,
        range_model: range_html_report,
    }


_init_handlers()


def __getattr__(name: str):
    """
    Ленивый импорт специализированных отчетов для обратной совместимости.
    """
    if name in ("recipe_html_report", "nomenclature_html_report", "range_html_report"):
        import importlib
        mod = importlib.import_module(f"Src.Logics.Reports.Html.{name}")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

