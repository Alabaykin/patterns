from Src.Core.abstract_report_factory import abstract_report_factory
from Src.Core.abstract_report import abstract_report
from Src.Dtos.report_type_enum import report_type_enum
from Src.Logics.text_report import text_report
from Src.Core.exception import arguments_exception


"""
Реализация фабрики для построения отчётов
"""
class report_factory(abstract_report_factory):
    __mapping: dict[report_type_enum, type[abstract_report]]

    def __init__(self):
        self.__mapping = {
            report_type_enum.TXT: text_report
        }

    def create(self, report_type: report_type_enum) -> abstract_report:
        if report_type not in self.__mapping:
            raise arguments_exception(f"Указанный тип отчета {report_type} не реализован!")

        report_class = self.__mapping[report_type]
        return report_class()
