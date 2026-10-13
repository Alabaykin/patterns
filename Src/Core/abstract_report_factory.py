from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from abc import ABC, abstractmethod
"""
Абстрактная фабрика отчетов
"""
class abstract_report_factory(ABC):

    """
    Подобрать и создать инстанс нужного отчёта
    """
    @abstractmethod
    def create(report_type:report_type_enum) -> abstract_report:
        pass