import json
import os
from datetime import datetime
import pytest
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Logics.storage_manager import storage_manager
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.recipe_model import recipe_model


class TestConvertFactory:
    """
    Тестирование фабрики convert_factory.
    """

    def test_factory_implements_interface(self):
        """
        Проверка реализации интерфейса абстрактной фабрики.
        """
        # Подготовка
        factory = convert_factory()

        # Действие и Проверка
        assert isinstance(factory, abstract_convert_factory)

    def test_factory_converters_property(self):
        """
        Проверка свойства converters и инкапсулированного маппинга типов.
        """
        # Подготовка
        factory = convert_factory()

        # Действие
        mapping = factory.converters

        # Проверка
        assert isinstance(mapping, dict)
        assert mapping[int] == basic_convertor
        assert mapping[float] == basic_convertor
        assert mapping[str] == basic_convertor
        assert mapping[bool] == basic_convertor
        assert mapping[datetime] == datetime_convertor
        assert mapping[abstract_entity] == reference_convertor

    def test_factory_create_instances(self):
        """
        Проверка фабричного метода create для различных типов и объектов.
        """
        # Подготовка
        factory = convert_factory()
        now = datetime.now()
        piece = range_model.create_piece()

        # Действие
        conv_int = factory.create(int)
        conv_str = factory.create("строка")
        conv_dt = factory.create(now)
        conv_entity = factory.create(piece)

        # Проверка
        assert isinstance(conv_int, basic_convertor)
        assert isinstance(conv_str, basic_convertor)
        assert isinstance(conv_dt, datetime_convertor)
        assert isinstance(conv_entity, reference_convertor)

    def test_factory_create_unregistered_type_raises(self):
        """
        Проверка генерации исключения при запросе конвертора для незарегистрированного типа.
        """
        # Подготовка
        factory = convert_factory()

        class UnknownType:
            pass

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            factory.create(UnknownType)

    def test_convert_primitives(self):
        """
        Проверка конвертации примитивного именованного поля.
        """
        # Подготовка
        factory = convert_factory()

        # Действие
        res = factory.convert("age", 25)

        # Проверка
        assert res == {"age": 25}

    def test_convert_list_of_elements(self):
        """
        Проверка конвертации списка элементов.
        """
        # Подготовка
        factory = convert_factory()
        items = [1, "two", 3.0]

        # Действие
        res = factory.convert("items", items)

        # Проверка
        assert res == {"items": [1, "two", 3.0]}

    def test_convert_dictionary(self):
        """
        Проверка конвертации словаря.
        """
        # Подготовка
        factory = convert_factory()
        meta = {"key": "val", "num": 10}

        # Действие
        res = factory.convert("meta", meta)

        # Проверка
        assert res == {"meta": {"key": "val", "num": 10}}

    def test_convert_single_object_returns_structure(self):
        """
        Проверка конвертации сущности напрямую без указания имени поля.
        """
        # Подготовка
        factory = convert_factory()
        recipe = recipe_model.create_dough_recipe()

        # Действие
        res = factory.convert(recipe)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Песочное тесто"
        assert isinstance(res["rows"], list)

    def test_convert_single_primitive_and_datetime(self):
        """
        Проверка сквозной конвертации одиночного числа и объекта datetime.
        """
        # Подготовка
        factory = convert_factory()
        now = datetime(2026, 10, 24, 15, 0, 0)

        # Действие
        res_num = factory.convert(100)
        res_date = factory.convert(now)

        # Проверка
        assert res_num == 100
        assert res_date == "2026-10-24T15:00:00"

    def test_serialize_deep_recipe_model(self):
        """
        Проверка глубокой сериализации составной модели рецепта.
        """
        # Подготовка
        factory = convert_factory()
        recipe = recipe_model.create_dough_recipe()

        # Действие
        serialized = factory.serialize(recipe)

        # Проверка
        assert isinstance(serialized, dict)
        assert serialized["name"] == "Песочное тесто"
        assert "rows" in serialized
        assert isinstance(serialized["rows"], list)

        first_row = serialized["rows"][0]
        assert "nomenclature" in first_row
        assert first_row["nomenclature"]["name"] == "Мука пшеничная"
        assert first_row["nomenclature"]["range"]["name"] == "кг"
        assert first_row["nomenclature"]["range"]["base_range"]["name"] == "гр"

    def test_generate_json_files(self):
        """
        Формирование эталонных файлов JSON для включения в Pull Request.
        """
        # Подготовка
        factory = convert_factory()
        sm = storage_manager()
        sm.load()

        json_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Json")
        os.makedirs(json_dir, exist_ok=True)

        files_to_generate = {
            "recipe.json": sm.recipes[0],
            "nomenclature.json": sm.nomenclatures[0],
            "range.json": sm.ranges[0],
            "warehouse.json": sm.warehouses[0],
            "group.json": sm.groups[0],
            "storage.json": sm.data,
        }

        # Действие
        for file_name, obj in files_to_generate.items():
            file_path = os.path.join(json_dir, file_name)
            serialized = factory.serialize(obj)
            with open(file_path, "w", encoding="utf-8") as fp:
                json.dump(serialized, fp, ensure_ascii=False, indent=2)

        # Проверка
        for file_name in files_to_generate:
            file_path = os.path.join(json_dir, file_name)
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

            with open(file_path, "r", encoding="utf-8") as fp:
                loaded = json.load(fp)
                assert isinstance(loaded, (dict, list))
