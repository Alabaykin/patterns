from Src.Logics.text_report import text_report
from Src.Models.range_model import range_model
from Src.Core.exception import arguments_exception


class range_text_report(text_report):
    """
    Формирование текстового отчета по единице измерения.
    """

    def build_header(self, source: range_model) -> str:
        if not isinstance(source, range_model):
            raise arguments_exception("Источник данных должен быть объектом range_model")
        return "Единица измерения\nКод | Наименование | Коэффициент | Базовая единица\n" + "-" * 60

    def build_body(self, source: range_model) -> str:
        base_name = source.base_range.name if source.base_range else "Базовая"
        return f"{source.id} | {source.name} | {source.coefficient} | {base_name}"
