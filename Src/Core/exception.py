class app_exception(Exception):
    """
    Базовое исключение для всех внутренних ошибок приложения.
    """
    __message: str = ""

    def __init__(self, message: str = ""):
        """
        Инициализация базового исключения.
        :param message: Описание ошибки
        """
        self.__message = str(message).strip() if message else ""
        super().__init__(self.__str__())

    @property
    def message(self) -> str:
        """
        Текст сообщения об ошибке.
        """
        return self.__message

    def __str__(self) -> str:
        return f"Ошибка приложения: {self.__message}"


class arguments_exception(app_exception):
    """
    Исключение, возникающее при некорректных аргументах или параметрах сущностей.
    """
    __field: str = ""

    def __init__(self, message: str = "", field: str = ""):
        """
        Инициализация исключения аргументов.
        :param message: Описание ошибки
        :param field: Наименование ошибочного поля/аргумента
        """
        self.__field = str(field).strip() if field else ""
        super().__init__(message)

    @property
    def field(self) -> str:
        """
        Имя ошибочного поля.
        """
        return self.__field

    def __str__(self) -> str:
        field_info = f" ({self.__field})" if self.__field else ""
        return f"Ошибка, некорректный аргумент{field_info}!\n{self.message}\n"


class operation_exception(app_exception):
    """
    Исключение, возникающее при нарушении бизнес-логики или невозможности выполнения операции.
    """
    def __init__(self, message: str = ""):
        """
        Инициализация исключения операции.
        :param message: Описание ошибки
        """
        super().__init__(message)

    def __str__(self) -> str:
        return f"Ошибка выполнения операции!\n{self.message}\n"
