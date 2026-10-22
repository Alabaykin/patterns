from Src.Core.abstract_report import abstract_report


class markdown_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате Markdown.
    Определяет метаданные формата (MIME-тип, расширение, режим вложения).
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        """
        MIME-тип контента отчёта в формате Markdown.
        """
        return "text/markdown"

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
        return "md"

    def _resolve_handler(self, source):
        """
        Поиск специализированного обработчика по типу доменной модели.
        """
        if type(self) is not markdown_report:
            return self
        handler_cls = self._handlers.get(type(source))
        if handler_cls:
            return handler_cls()
        return self


def _init_handlers():
    from Src.Models.recipe_model import recipe_model
    from Src.Models.nomenclature_model import nomenclature_model
    from Src.Models.range_model import range_model
    from Src.Logics.Reports.Markdown.recipe_markdown_report import recipe_markdown_report
    from Src.Logics.Reports.Markdown.nomenclature_markdown_report import nomenclature_markdown_report
    from Src.Logics.Reports.Markdown.range_markdown_report import range_markdown_report

    markdown_report._handlers = {
        recipe_model: recipe_markdown_report,
        nomenclature_model: nomenclature_markdown_report,
        range_model: range_markdown_report,
    }


_init_handlers()


def __getattr__(name: str):
    """
    Ленивый импорт специализированных отчетов для обратной совместимости.
    """
    if name in ("recipe_markdown_report", "nomenclature_markdown_report", "range_markdown_report"):
        import importlib
        mod = importlib.import_module(f"Src.Logics.Reports.Markdown.{name}")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

