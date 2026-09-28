from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception


class organization_model(abstract_entity):
    """
    Модель организации (контрагента или филиала сети).
    """
    _inn: str = ""
    _bik: str = ""
    _account: str = ""
    _ownership_type: str = ""

    def __init__(self, name: str, inn: str, bik: str, account: str, ownership_type: str):
        """
        Инициализация организации.
        :param name: Наименование организации (до 50 символов)
        :param inn: ИНН организации (10 или 12 цифр)
        :param bik: БИК банка (9 цифр)
        :param account: Расчетный счет (20 цифр)
        :param ownership_type: Форма собственности (например, "ООО", "ИП")
        """
        self.name = name
        self.inn = inn
        self.bik = bik
        self.account = account
        self.ownership_type = ownership_type

    @property
    def inn(self) -> str:
        """
        ИНН организации (10 или 12 цифр).
        """
        return self._inn

    @inn.setter
    def inn(self, value: str) -> None:
        """
        Установка ИНН организации.
        """
        if not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) not in (10, 12):
            raise arguments_exception("ИНН должен состоять из 10 или 12 цифр", "inn")
        self._inn = value.strip()

    @property
    def bik(self) -> str:
        """
        БИК банка (9 цифр).
        """
        return self._bik

    @bik.setter
    def bik(self, value: str) -> None:
        """
        Установка БИК банка.
        """
        if not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) != 9:
            raise arguments_exception("БИК должен состоять ровно из 9 цифр", "bik")
        self._bik = value.strip()

    @property
    def account(self) -> str:
        """
        Расчетный счет (20 цифр).
        """
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        """
        Установка расчетного счета.
        """
        if not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) != 20:
            raise arguments_exception("Счет должен состоять ровно из 20 цифр", "account")
        self._account = value.strip()

    @property
    def ownership_type(self) -> str:
        """
        Форма собственности (например, 'ООО', 'ИП').
        """
        return self._ownership_type

    @ownership_type.setter
    def ownership_type(self, value: str) -> None:
        """
        Установка формы собственности.
        """
        if not isinstance(value, str) or not value.strip():
            raise arguments_exception("Форма собственности должна быть непустой строкой", "ownership_type")
        if len(value.strip()) > 50:
            raise arguments_exception("Форма собственности не должна превышать 50 символов", "ownership_type")
        self._ownership_type = value.strip()

