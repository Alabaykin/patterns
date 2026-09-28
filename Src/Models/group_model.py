from Src.Core.abstract_entity import abstract_entity


class group_model(abstract_entity):
    """
    Модель группы номенклатуры.
    """
    def __init__(self, name: str):
        """
        Инициализация группы номенклатуры.
        :param name: Наименование группы (до 50 символов)
        """
        self.name = name
