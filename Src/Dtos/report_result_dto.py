from Src.Core.abstract_entity import abstract_entity
from Src.Core.validator import validator

"""
Модель для хранения результата формирования отчёта.
"""
class report_result_dto(abstract_entity):
    __text: str = ""
    __binary: list = []

    def __init__(self, text: str = "", binary: list = None):
        if binary is None:
            binary = []
        self.__text = text if len(binary) == 0 else ""
        self.__binary = binary if len(text.strip()) == 0 else []

    """
    Текстовый результат.
    """
    @property
    def text(self) -> str:
        return self.__text

    """
    Бинарный результат.
    """
    @property
    def binary(self) -> list:
        return self.__binary

    @text.setter
    def text(self, value: str) -> None:
        validator.validate(value, str)
        self.__text = value
        self.__binary = []

    @binary.setter
    def binary(self, value: list) -> None:
        validator.validate(value, list)
        self.__text = ""
        self.__binary = value