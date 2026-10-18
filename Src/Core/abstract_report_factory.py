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
    def create(self, report_type: report_type_enum, entity_type: str = "") -> abstract_report:
        pass

    """
    Создать отчет
    """
    @abstractmethod
    def create_default(self, entity_type: str = "") -> abstract_report:
        pass

