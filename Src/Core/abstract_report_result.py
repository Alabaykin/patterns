from abc import ABC, abstractmethod

"""
Абстрактный класс для формирования отчётов
"""
class abstract_report(ABC):

    @abstractmethod
    def build(self, source):
        """
        Метод формирования отчёта
        """
        pass