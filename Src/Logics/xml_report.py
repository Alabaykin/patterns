from Src.Core.abstract_report import abstract_report


class xml_report(abstract_report):
    """
    Базовый класс формирования отчёта в формате XML.
    Определяет метаданные формата (MIME-тип, расширение, режим вложения).
    """

    _handlers = {}

    @property
    def mimetype(self) -> str:
        """
        MIME-тип контента отчёта в формате XML.
        """
        return "application/xml"

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
        return "xml"

    def _resolve_handler(self, source):
        """
        Поиск специализированного обработчика по типу доменной модели.
        """
        if type(self) is not xml_report:
            return self
        handler_cls = self._handlers.get(type(source))
        if handler_cls:
            return handler_cls()
        return self


def _init_handlers():
    from Src.Models.recipe_model import recipe_model
    from Src.Models.nomenclature_model import nomenclature_model
    from Src.Models.range_model import range_model
    from Src.Logics.Reports.Xml.recipe_xml_report import recipe_xml_report
    from Src.Logics.Reports.Xml.nomenclature_xml_report import nomenclature_xml_report
    from Src.Logics.Reports.Xml.range_xml_report import range_xml_report

    xml_report._handlers = {
        recipe_model: recipe_xml_report,
        nomenclature_model: nomenclature_xml_report,
        range_model: range_xml_report,
    }


_init_handlers()


def __getattr__(name: str):
    """
    Ленивый импорт специализированных отчетов для обратной совместимости.
    """
    if name in ("recipe_xml_report", "nomenclature_xml_report", "range_xml_report"):
        import importlib
        mod = importlib.import_module(f"Src.Logics.Reports.Xml.{name}")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

