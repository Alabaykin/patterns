from Src.Core.abstract_deserialize_factory import abstract_deserialize_factory
from Src.Core.abstract_deserializer import abstract_deserializer
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.basic_entity_deserializer import basic_entity_deserializer
from Src.Logics.nomenclature_deserializer import nomenclature_deserializer
from Src.Logics.range_deserializer import range_deserializer
from Src.Logics.recipe_deserializer import recipe_deserializer
from Src.Logics.recipe_row_deserializer import recipe_row_deserializer
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model
from Src.Models.recipe_model import recipe_model
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.warehouse_model import warehouse_model


class deserialize_factory(abstract_deserialize_factory):
    """
    Фабрика подбора десериализаторов по внутреннему словарю типов моделей.
    """

    def __init__(self):
        """
        Инициализация обработчиков справочников, рецептов и строк рецептов.
        """
        super().__init__()
        self.__mapping: dict[type[abstract_entity], abstract_deserializer] = {
            group_model: basic_entity_deserializer(group_model),
            warehouse_model: basic_entity_deserializer(warehouse_model),
            range_model: range_deserializer(self),
            nomenclature_model: nomenclature_deserializer(self),
            recipe_model: recipe_deserializer(self),
            recipe_row_model: recipe_row_deserializer(self),
        }

    @property
    def mapping(self) -> dict[type[abstract_entity], abstract_deserializer]:
        """
        Получение копии словаря сопоставления типов моделей и десериализаторов.
        """
        return self.__mapping.copy()

    def create(self, model_type: type[abstract_entity]) -> abstract_deserializer:
        """
        Подбор обработчика указанной модели без выполнения десериализации.
        """
        if not isinstance(model_type, type):
            raise arguments_exception("Ожидается тип доменной модели", "model_type")
        if model_type not in self.__mapping:
            raise arguments_exception(
                f"Для типа '{model_type.__name__}' десериализатор не зарегистрирован", "model_type"
            )
        return self.__mapping[model_type]
