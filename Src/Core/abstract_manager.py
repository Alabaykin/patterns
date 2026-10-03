from abc import ABC


"""
Абстрактный класс для реализации загрузки и обработки данных
"""
class abstract_manager(ABC):
    # Полный путь к файлу данных
    __file_name:str = ""
    # Флаг, указывающий, что данные загружены и обработаны
    __is_loaded:bool = False
    # Загруженные данные
    __data:list = []

    """
    Загружает данные из файла. 
    """    
    def load(self,file_name:str = "") -> None:
        pass


    """
    Обрабатывает загруженные данные.
    """
    def convert(self) -> bool:
        return False


    """
    Флаг данные подготовленные
    """
    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded