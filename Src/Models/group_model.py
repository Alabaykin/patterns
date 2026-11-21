from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class group_model(abstract_entity):
    """
    Модель группы номенклатуры.
    """
    _parent: group_model = None

    def __init__(self, name: str, parent: group_model = None):
        """
        Инициализация группы номенклатуры.
        :param name: Наименование группы (до 50 символов)
        """
        self.name = name
        self.parent = parent

    def get_reference_fields(self) -> list[tuple]:
        """Родительская группа для вложенной структуры справочника."""
        return [(self, "parent")]

    @property
    def parent(self) -> group_model | None:
        """Группа-владелец; у корневой группы отсутствует."""
        return self._parent

    @parent.setter
    def parent(self, value: group_model | None) -> None:
        if value is not None and not isinstance(value, group_model):
            raise arguments_exception("Ожидается родительская группа", "parent")
        self._parent = value

    @staticmethod
    def create_raw() -> group_model:
        """
        Фабричный метод создания группы 'Сырье'.
        """
        return group_model("Сырье")

    @staticmethod
    def create_semi() -> group_model:
        """
        Фабричный метод создания группы 'Полуфабрикаты'.
        """
        return group_model("Полуфабрикаты")

    @staticmethod
    def create_dishes() -> group_model:
        """
        Фабричный метод создания группы 'Блюда'.
        """
        return group_model("Блюда")

    @staticmethod
    def create_package() -> group_model:
        """
        Фабричный метод создания группы 'Упаковка'.
        """
        return group_model("Упаковка")
