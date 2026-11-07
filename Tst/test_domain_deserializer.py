import json
import pytest
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.deserialize_factory import deserialize_factory
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.organization_model import organization_model
from Src.Models.range_model import range_model


def test_restore_single_nomenclature_by_json_type():
    """
    Проверка восстановления номенклатуры и её связей по типам из JSON.
    """
    # Подготовка
    source = nomenclature_model.create_flour()
    serializer = convert_factory()
    data = json.loads(json.dumps(serializer.serialize(source), ensure_ascii=False))
    factory = deserialize_factory()

    # Действие
    restored = factory.deserialize(data)

    # Проверка
    assert data["type"] == "Src.Models.nomenclature_model.nomenclature_model"
    assert data["group"]["type"] == source.group.type
    assert data["range"]["base_range"]["type"] == source.range.base_range.type
    assert isinstance(restored, nomenclature_model)
    assert isinstance(restored.group, group_model)
    assert isinstance(restored.range, range_model)
    assert isinstance(restored.range.base_range, range_model)
    assert restored.id == source.id
    assert restored.range.base_range.id == source.range.base_range.id
    assert serializer.serialize(restored) == data


def test_restore_model_without_its_own_deserializer():
    """
    Проверка восстановления экспортируемой модели общим обработчиком без отдельного класса.
    """
    # Подготовка
    source = organization_model("Ромашка", "1234567890", "123456789", "12345678901234567890", "ООО")
    serializer = convert_factory()
    data = serializer.serialize(source)
    factory = deserialize_factory()

    # Действие
    restored = factory.deserialize(data)

    # Проверка
    assert isinstance(restored, organization_model)
    assert restored is not source
    assert serializer.serialize(restored) == data


def test_reject_unregistered_json_type():
    """
    Проверка запрета создания объекта по имени класса вне списка моделей.
    """
    # Подготовка
    data = {"type": "pathlib.Path", "name": "Неподдерживаемый тип"}
    factory = deserialize_factory()

    # Действие и Проверка
    with pytest.raises(arguments_exception) as error:
        factory.deserialize(data)
    assert error.value.field == "type"
