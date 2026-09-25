from Src.Core.abstract_entity import abstract_entity


class warehouse_model(abstract_entity):
    """
    Модель склада.
    """
    def __init__(self, name: str):
        """
        Инициализация склада.
        :param name: Наименование склада (до 50 символов)
        """
        self.name = name
