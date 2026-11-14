import json
from pathlib import Path

from Src.Core.abstract_manager import abstract_manager
from Src.Core.exception import arguments_exception, operation_exception
from Src.Models.settings_model import settings_model
from Src.Logics.deserialize_factory import deserialize_factory


class settings_manager(abstract_manager):
    """Загружает настройки общим десериализатором."""

    __default_file_name = Path(__file__).resolve().parents[2] / "settings.json"
    _settings: settings_model = None
    __is_loaded = False

    def __new__(cls):
        """Получить единственный экземпляр менеджера настроек."""
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def load(self, file_name: str = "") -> None:
        """Прочитать файл и применить настройки только после полной успешной проверки."""
        if not isinstance(file_name, str):
            raise arguments_exception("Имя файла должно быть строкой", "file_name")
        path = file_name.strip() or self.__default_file_name
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            candidate = deserialize_factory().deserialize(data)
            if not isinstance(candidate, settings_model):
                raise arguments_exception("Ожидается модель настроек", "type")
        except (OSError, UnicodeError, ValueError, arguments_exception) as error:
            raise operation_exception(f"Ошибка при загрузке настроек '{path}': {error}") from error
        self.__data = data
        if self._settings is None:
            self._settings = candidate
        else:
            self._settings.replace_state(candidate)
        self.__is_loaded = True

    def convert(self) -> bool:
        """Повторно преобразовать ранее прочитанные данные тем же десериализатором."""
        if not isinstance(self.__data, dict):
            return False
        candidate = deserialize_factory().deserialize(self.__data)
        if not isinstance(candidate, settings_model):
            raise arguments_exception("Ожидается модель настроек", "type")
        if self._settings is None:
            self._settings = candidate
        else:
            self._settings.replace_state(candidate)
        return True

    @property
    def is_loaded(self) -> bool:
        """Признак успешной загрузки настроек."""
        return self.__is_loaded

    @property
    def settings(self) -> settings_model:
        """Последние успешно загруженные настройки."""
        return self._settings
