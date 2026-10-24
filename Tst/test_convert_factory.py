import io
import json
import os
from datetime import datetime
import pytest
from Src.Core.abstract_convert_factory import abstract_convert_factory
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
        # Подготовка
        f = convert_factory()

        # Действие и Проверка
        assert isinstance(f, abstract_convert_factory)

    def test_get_convertors_mapping(self):
        # Подготовка
        f = convert_factory()
        now = datetime.now()
        piece = range_model.create_piece()

        # Действие и Проверка
        assert isinstance(f.get_convertor_for(123), basic_convertor)
        assert isinstance(f.get_convertor_for("abc"), basic_convertor)
        assert isinstance(f.get_convertor_for(now), datetime_convertor)
        assert isinstance(f.get_convertor_for(piece), reference_convertor)

    def test_create_alias(self):
        # Подготовка
        f = convert_factory()

        # Действие
        conv = f.create(float)

        # Проверка
        assert isinstance(conv, basic_convertor)

    def test_register_type_custom(self):
        # Подготовка
        f = convert_factory()

        class CustomClass:
            pass

        class CustomConv(basic_convertor):
            pass

        # Действие
        f.register_type(CustomClass, CustomConv)

        # Проверка
        assert isinstance(f.get_convertor_for(CustomClass), CustomConv)

    def test_register_type_invalid_raises(self):
        # Подготовка
        f = convert_factory()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            f.register_type("not_type", basic_convertor)
        with pytest.raises(arguments_exception):
            f.register_type(dict, object)

    def test_unregistered_type_raises(self):
        # Подготовка
        f = convert_factory()

        class Unknown:
            pass

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            f.get_convertor_for(Unknown)

    def test_convert_primitives(self):
        # Подготовка
        f = convert_factory()

        # Действие
        res = f.convert("age", 25)

        # Проверка
        assert res == {"age": 25}

    def test_convert_list_of_elements(self):
        # Подготовка
        f = convert_factory()
        items = [1, "two", 3.0]

        # Действие
        res = f.convert("items", items)

        # Проверка
        assert res == {"items": [1, "two", 3.0]}

    def test_convert_dictionary(self):
        # Подготовка
        f = convert_factory()
        meta = {"key": "val", "num": 10}

        # Действие
        res = f.convert("meta", meta)

        # Проверка
        assert res == {"meta": {"key": "val", "num": 10}}

    def test_convert_single_object_returns_structure(self):
        # Подготовка
        f = convert_factory()
        recipe = recipe_model.create_dough_recipe()

        # Действие
        res = f.convert(recipe)

        # Проверка
        assert isinstance(res, dict)
        assert res["name"] == "Песочное тесто"
        assert isinstance(res["rows"], list)

    def test_convert_single_primitive_and_datetime(self):
        # Подготовка
        f = convert_factory()
        now = datetime(2026, 10, 24, 15, 0, 0)

        # Действие
        res_num = f.convert(100)
        res_date = f.convert(now)

        # Проверка
        assert res_num == 100
        assert res_date == "2026-10-24T15:00:00"

    def test_serialize_deep_recipe_model(self):
        # Подготовка
        f = convert_factory()
        recipe = recipe_model.create_dough_recipe()

        # Действие
        serialized = f.serialize(recipe)

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

    def test_to_json_valid_formatting(self):
        # Подготовка
        f = convert_factory()
        grp = group_model.create_raw()

        # Действие
        json_str = f.to_json(grp)

        # Проверка
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert parsed["name"] == "Сырье"

    def test_dump_to_stream(self):
        # Подготовка
        f = convert_factory()
        kg = range_model.create_kilogramm()
        stream = io.StringIO()

        # Действие
        f.dump(kg, stream)
        val = stream.getvalue()

        # Проверка
        assert "кг" in val
        parsed = json.loads(val)
        assert parsed["name"] == "кг"

    def test_generate_json_files(self):
        # Подготовка
        f = convert_factory()
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
            with open(file_path, "w", encoding="utf-8") as fp:
                f.dump(obj, fp, indent=2)

        # Проверка
        for file_name in files_to_generate:
            file_path = os.path.join(json_dir, file_name)
            assert os.path.exists(file_path)
            assert os.path.getsize(file_path) > 0

            with open(file_path, "r", encoding="utf-8") as fp:
                loaded = json.load(fp)
                assert isinstance(loaded, (dict, list))
