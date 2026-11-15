from Src import Models
from Src.Core.abstract_entity import abstract_entity
from Src.Logics.entity_registry import entity_registry
from Src.Logics.storage_manager import storage_manager


def test_success_registry_discovers_new_model():
    """Дополнительная коллекция обнаруживается по аннотации без вызова геттера."""
    # Подготовка
    class supplier_model(abstract_entity):
        """Дополнительный справочник для проверки расширения набора моделей."""

    class extended_storage(storage_manager):
        """Хранилище с дополнительной коллекцией для проверки рефлексии."""

        @property
        def suppliers(self) -> list[supplier_model]:
            raise AssertionError("Реестр не должен читать содержимое коллекции")

    # Действие
    models = entity_registry.get_models(extended_storage)

    # Проверка
    assert models["suppliers"] is supplier_model
    assert models["groups"] is Models.group_model
    assert Models.settings_model not in models.values()
    assert Models.organization_model not in models.values()
    assert Models.recipe_row_model not in models.values()
