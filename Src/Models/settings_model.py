from Src.Core.abstract_entity import abstract_entity
from Src.Core.validator import validator
from Src.Models.organization_model import organization_model


class settings_model(abstract_entity):
    # Карточка организации
    __organization: organization_model = None
    # Наименование руководителя
    __boss_name: str = ""
    # Наименование главного бухгалтера
    __account_name: str = ""

    """
    Карточка организации
    """
    @property
    def organization(self) -> organization_model:
        return self.__organization

    @organization.setter
    def organization(self, value: organization_model) -> None:
        validator.validate(value, organization_model)
        self.__organization = value

    @property
    def company(self) -> organization_model:
        """
        Алиас для карточки организации
        """
        return self.__organization

    @company.setter
    def company(self, value: organization_model) -> None:
        self.organization = value

    """
    Наименование руководителя
    """
    @property
    def boss_name(self) -> str:
        return self.__boss_name

    @boss_name.setter
    def boss_name(self, value: str) -> None:
        validator.validate(value, str, 255)
        self.__boss_name = value.strip()

    """
    Наименование главного бухгалтера
    """
    @property
    def account_name(self) -> str:
        return self.__account_name

    @account_name.setter
    def account_name(self, value: str) -> None:
        validator.validate(value, str, 255)
        self.__account_name = value.strip()

    """
    Флаг первого старта
    """
    __is_first: bool = True

    @property
    def is_first(self) -> bool:
        return self.__is_first

    @is_first.setter
    def is_first(self, value: bool) -> None:
        validator.validate(value, bool)
        self.__is_first = value