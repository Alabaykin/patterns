
class arguments_exception(Exception):
    __stack_trace:str = ""
    __message:str = ""
    __field:str = ""
    
    def __init__(self, field:str, message:str = "", stack_trace:str = ""):
        self.__field = field
        self.__message = message.strip()
        self.__stack_trace = stack_trace.strip()

    def __str__(self):
        return f"Ошибка, некорректный аргумент {self.__field}! ({self.__field})\n{self.__message}\n"        