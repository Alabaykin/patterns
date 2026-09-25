class arguments_exception(Exception):
    """
    Исключение, возникающее при некорректных аргументах или параметрах сущностей.
    """
    __field: str = ""
    __message: str = ""
    __stack_trace: str = ""

    def __init__(self, message: str = "", field: str = "", stack_trace: str = ""):
        """
        Инициализация исключения.
        :param message: Описание ошибки
        :param field: Наименование ошибочного поля/аргумента
        :param stack_trace: Стек вызовов
        """
        self.__message = str(message).strip() if message else ""
        self.__field = str(field).strip() if field else ""
        self.__stack_trace = str(stack_trace).strip() if stack_trace else ""
        super().__init__(self.__str__())

    def __str__(self) -> str:
        """
        Строковое представление ошибки.
        """
        field_info = f" ({self.__field})" if self.__field else ""
        return f"Ошибка, некорректный аргумент{field_info}!\n{self.__message}\n"
