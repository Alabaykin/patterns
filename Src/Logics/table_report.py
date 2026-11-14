from abc import abstractmethod

from Src.Core.abstract_report import abstract_report
from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_data_dto import report_data_dto
from Src.Dtos.report_result_dto import report_result_dto
from Src.Logics.report_data_builder import report_data_builder


class table_report(abstract_report):
    """Общий шаблон: извлечение данных, оформление и упаковка результата."""

    def build(self, source: abstract_entity) -> report_result_dto:
        """Подготовить DTO единожды и передать его построителю выбранного формата."""
        data = report_data_builder().build(source)
        content = self._render(data)
        if self.is_attachment:
            return report_result_dto(binary=list(content.encode("utf-8")))
        return report_result_dto(text=content)

    @abstractmethod
    def _render(self, data: report_data_dto) -> str:
        """Оформить подготовленные данные без обращения к доменной модели."""
        pass
