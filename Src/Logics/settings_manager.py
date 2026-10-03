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
        if not isinstance(self.__data, dict):
            return False

        if self._settings is None:
            self._settings = settings_model()
            
        company_name = self.__data.get("company_name", "")
        inn = str(self.__data.get("inn", ""))
        bik = str(self.__data.get("bik", ""))
        account = str(self.__data.get("account", ""))
        ownership_type = self.__data.get("ownership_type", "")

        from Src.Models.organization_model import organization_model
        organization = organization_model(
            name=company_name,
            inn=inn,
            bik=bik,
            account=account,
            ownership_type=ownership_type
        )
        self._settings.organization = organization
        boss_name = self.__data.get("boss_name", "")
        if boss_name:
            self._settings.boss_name = boss_name

        account_name = self.__data.get("account_name", "")
        if account_name:
            self._settings.account_name = account_name

        if "is_first" in self.__data:
            self._settings.is_first = bool(self.__data["is_first"])

        return True

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    @property
    def settings(self)-> settings_model:
        return self._settings