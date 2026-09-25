from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Models.group_model import group_model
from Src.Models.range_model import range_model


class nomenclature_model(abstract_entity):
    """
    Модель номенклатуры (сырье, блюдо, полуфабрикат, товар).
    """
    _full_name: str = ""
    _group: group_model = None
    _range: range_model = None

    def __init__(self, name: str, full_name: str, group: group_model, range: range_model):
        """
        Инициализация номенклатуры.
        :param name: Краткое наименование (до 50 символов)
        :param full_name: Полное наименование (до 255 символов)
        :param group: Группа номенклатуры (group_model)
        :param range: Единица измерения (range_model)
        """
        self.name = name
        self.full_name = full_name
        self.group = group
        self.range = range

    @property
    def full_name(self) -> str:
        """
        Полное наименование номенклатуры (до 255 символов).
        """
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        """
        Установка полного наименования.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Полное наименование должно быть непустой строкой", "full_name")
        if len(value.strip()) > 255:
            raise arguments_exception("Полное наименование не должно превышать 255 символов", "full_name")
        self._full_name = value.strip()

    @property
    def group(self) -> group_model:
        """
        Группа номенклатуры.
        """
        return self._group

    @group.setter
    def group(self, value: group_model) -> None:
        """
        Установка группы номенклатуры.
        """
        if not isinstance(value, group_model):
            raise arguments_exception("Группа номенклатуры должна быть объектом group_model", "group")
        self._group = value

    @property
    def range(self) -> range_model:
        """
        Единица измерения номенклатуры.
        """
        return self._range

    @range.setter
    def range(self, value: range_model) -> None:
        """
        Установка единицы измерения номенклатуры.
        """
        if not isinstance(value, range_model):
            raise arguments_exception("Единица измерения должна быть объектом range_model", "range")
        self._range = value
