from datetime import date, datetime
import pytest
from Src.Core.abstract_convertor import abstract_convertor
from Src.Core.exception import arguments_exception
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
from Src.Models.range_model import range_model
from Src.Models.group_model import group_model
from Src.Models.nomenclature_model import nomenclature_model


class TestAbstractConvertorContract:
    """
    Тестирование контракта абстрактного класса abstract_convertor.
    """

    def test_cannot_instantiate_abstract(self):
        # Подготовка / Действие / Проверка
        with pytest.raises(TypeError):
            abstract_convertor()

    def test_has_abstract_method_convert(self):
        # Подготовка
        target_class = abstract_convertor

        # Действие
        abstract_methods = target_class.__abstractmethods__

        # Проверка
        assert "convert" in abstract_methods


class TestBasicConvertor:
    """
    Тесты для basic_convertor.
    """

    def test_inheritance(self):
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        assert isinstance(conv, abstract_convertor)

    @pytest.mark.parametrize(
        "field, val, expected",
        [
            ("quantity", 5, {"quantity": 5}),
            ("ratio", 1.25, {"ratio": 1.25}),
            ("title", "Сахар", {"title": "Сахар"}),
            ("is_ready", False, {"is_ready": False}),
            ("comment", None, {"comment": None}),
        ],
        ids=["int", "float", "str", "bool", "none"],
    )
    def test_valid_primitive_conversion(self, field, val, expected):
        # Подготовка
        conv = basic_convertor()

        # Действие
        res = conv.convert(field, val)

        # Проверка
        assert res == expected

    def test_single_arg_conversion(self):
        # Подготовка
        conv = basic_convertor()

        # Действие
        res_num = conv.convert(42)
        res_str = conv.convert("test")

        # Проверка
        assert res_num == {"numeric": 42}
        assert res_str == {"value": "test"}

    def test_invalid_field_name_type_raises(self):
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert(123, "val")

    def test_empty_field_name_raises(self):
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("   ", "val")

    def test_non_primitive_value_raises(self):
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("items", [1, 2, 3])


class TestDatetimeConvertor:
    """
    Тесты для datetime_convertor.
    """

    def test_inheritance(self):
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        assert isinstance(conv, abstract_convertor)

    def test_datetime_format(self):
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 22, 19, 30, 15)

        # Действие
        res = conv.convert("timestamp", dt)

        # Проверка
        assert res == {"timestamp": "2026-10-22T19:30:15"}

    def test_date_format(self):
        # Подготовка
        conv = datetime_convertor()
        d = date(2026, 10, 22)

        # Действие
        res = conv.convert("day", d)

        # Проверка
        assert res == {"day": "2026-10-22"}

    def test_single_arg_conversion(self):
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 24, 12, 0, 0)

        # Действие
        res = conv.convert(dt)

        # Проверка
        assert res == {"datetime": "2026-10-24T12:00:00"}

    def test_invalid_value_type_raises(self):
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("date", "2026-10-22")

    def test_empty_field_raises(self):
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("", date.today())


class TestReferenceConvertor:
    """
    Тесты для reference_convertor.
    """

    def test_inheritance(self):
        # Подготовка
        conv = reference_convertor()

        # Действие & Проверка
        assert isinstance(conv, abstract_convertor)

    def test_convert_single_model(self):
        # Подготовка
        conv = reference_convertor()
        grp = group_model.create_raw()

        # Действие
        res = conv.convert("group", grp)

        # Проверка
        assert "group" in res
        data = res["group"]
        assert data["id"] == grp.id
        assert data["name"] == grp.name

    def test_convert_single_model_without_field_name(self):
        """
        Проверка возврата словаря в формате ключ - наименование поля, значение - данные поля
        при передаче объекта напрямую в convert(obj).
        """
        # Подготовка
        conv = reference_convertor()
        grp = group_model.create_raw()

        # Действие
        res = conv.convert(grp)

        # Проверка
        assert isinstance(res, dict)
        assert "id" in res
        assert "name" in res
        assert res["id"] == grp.id
        assert res["name"] == grp.name

    def test_convert_recursive_nested_model(self):
        # Подготовка
        conv = reference_convertor()
        kg = range_model.create_kilogramm()

        # Действие
        res = conv.convert("range", kg)

        # Проверка
        data = res["range"]
        assert data["name"] == "кг"
        assert data["coefficient"] == 1000.0
        assert "base_range" in data
        assert data["base_range"]["name"] == "гр"
        assert data["base_range"]["coefficient"] == 1.0

    def test_circular_reference_does_not_crash(self):
        # Подготовка
        conv = reference_convertor()
        item = range_model.create_piece()
        item.base_range = item  # Цикл на себя

        # Действие
        res = conv.convert("cyclic", item)

        # Проверка
        assert res["cyclic"]["base_range"]["id"] == item.id
        assert res["cyclic"]["base_range"]["name"] == item.name

    def test_non_entity_argument_raises(self):
        # Подготовка
        conv = reference_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("bad", "не сущность")
        with pytest.raises(arguments_exception):
            conv.convert("не сущность")
