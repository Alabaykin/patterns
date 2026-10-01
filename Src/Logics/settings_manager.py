from Src.Core.abstract_manager import abstract_manager
from Src.Core.validator import validator, operation_exception
import json
from Src.Models.settings_model import settings_model

class settings_manager(abstract_manager):
    __default_file_name:str = "settings.json"
    _settings:settings_model = None
    __is_loaded:bool = False
    """
    Загружает данные из файла
    """


    # Singletone
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(settings_manager, cls).__new__(cls)
        return cls.instance


    
    def load(self,file_name=""):
        inner_file_name = file_name if file_name.strip() != "" else self.__default_file_name
        validator.validate(inner_file_name,str)


        try:
            with open(inner_file_name, "r", encoding="utf-8") as file:
                self.__data = json.load(file)
                self.__is_loaded = self.convert()
        except Exception as ex:
            raise operation_exception(f"Ошибка при загрузке данных из файла {inner_file_name}: {str(ex)}")

    def convert(self) -> bool:
        if self._settings is None:
            self._settings = settings_model()
        return True

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    @property
    def settings(self)-> settings_model:
        return self._settings