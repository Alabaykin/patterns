from Src.Core.exception import arguments_exception, operation_exception

"""
Набор проверок данных
"""
class validator:

    @staticmethod
    def validate( value, type_, len_= None):
        """
            Валидация аргумента по типу и длине
        Args:
            value (any): Аргумент
            type_ (object): Ожидаемый тип
            len_ (int): Максимальная длина
        Raises:
            arguent_exception: Некорректный тип
            arguent_exception: Неулевая длина
            arguent_exception: Некорректная длина аргумента
        Returns:
            True или Exception
        """

        if value is None:
            raise arguments_exception("Пустой аргумент")

        # Проверка типа
        if not isinstance(value, type_):
            raise arguments_exception(f"Некорректный тип!\nОжидается {type_}. Текущий тип {type(value)}")

        # Проверка аргумента
        if len(str(value).strip()) == 0:
            raise arguments_exception("Пустой аргумент")

        if len_ is not None and len(str(value).strip()) > len_:
            raise arguments_exception("Некорректная длина аргумента")

        return True