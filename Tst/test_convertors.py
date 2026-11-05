from datetime import date, datetime, timedelta, timezone
from types import SimpleNamespace
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
        """
        Проверка запрета создания экземпляра абстрактного конвертора.
        """
        # Подготовка / Действие / Проверка
        with pytest.raises(TypeError):
            abstract_convertor()

    def test_has_abstract_method_convert(self):
        """
        Проверка наличия абстрактного метода convert.
        """
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
        """
        Проверка наследования от абстрактного конвертора.
        """
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
        """
        Проверка преобразования простых значений в словарь именованного поля.
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        res = conv.convert(field, val)

        # Проверка
        assert res == expected

    def test_single_arg_conversion(self):
        """
        Проверка преобразования значения без указания имени поля.
        """
        # Подготовка
        conv = basic_convertor()

        # Действие
        res_num = conv.convert(42)
        res_str = conv.convert("test")

        # Проверка
        assert res_num == {"numeric": 42}
        assert res_str == {"value": "test"}

    def test_invalid_field_name_type_raises(self):
        """
        Проверка исключения при неверном типе имени поля.
        """
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert(123, "val")

    def test_empty_field_name_raises(self):
        """
        Проверка исключения при пустом имени поля.
        """
        # Подготовка
        conv = basic_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("   ", "val")

    def test_non_primitive_value_raises(self):
        """
        Проверка исключения при передаче составного значения конвертору простых типов.
        """
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
        """
        Проверка наследования от абстрактного конвертора.
        """
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        assert isinstance(conv, abstract_convertor)

    def test_datetime_format(self):
        """
        Проверка преобразования даты и времени в формат ISO 8601.
        """
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 22, 19, 30, 15)

        # Действие
        res = conv.convert("timestamp", dt)

        # Проверка
        assert res == {"timestamp": "2026-10-22T19:30:15"}

    def test_date_format(self):
        """
        Проверка преобразования даты в формат ISO 8601.
        """
        # Подготовка
        conv = datetime_convertor()
        d = date(2026, 10, 22)

        # Действие
        res = conv.convert("day", d)

        # Проверка
        assert res == {"day": "2026-10-22"}

    def test_single_arg_conversion(self):
        """
        Проверка преобразования значения без указания имени поля.
        """
        # Подготовка
        conv = datetime_convertor()
        dt = datetime(2026, 10, 24, 12, 0, 0)

        # Действие
        res = conv.convert(dt)

        # Проверка
        assert res == {"datetime": "2026-10-24T12:00:00"}

    def test_invalid_value_type_raises(self):
        """
        Проверка исключения при передаче значения неподдерживаемого типа.
        """
        # Подготовка
        conv = datetime_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("date", "2026-10-22")

    def test_empty_field_raises(self):
        """
        Проверка исключения при пустом имени поля даты.
        """
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
        """
        Проверка наследования от абстрактного конвертора.
        """
        # Подготовка
        conv = reference_convertor()

        # Действие и Проверка
        assert isinstance(conv, abstract_convertor)

    def test_convert_single_model(self):
        """
        Проверка преобразования сущности в словарь именованного поля.
        """
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
        """
        Проверка преобразования сущности с вложенной базовой единицей измерения.
        """
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

    @pytest.mark.parametrize("create", [range_model.create_gramm, range_model.create_kilogramm])
    def test_base_range_is_the_only_base_field(self, create):
        """
        Проверка сериализации базовой единицы без дублирующего поля base.
        """
        # Подготовка
        item = create()

        # Действие
        data = reference_convertor().convert(item)

        # Проверка
        assert "base" not in data
        assert "base_range" in data
        if item.base_range is None:
            assert data["base_range"] is None
        else:
            assert data["base_range"]["name"] == item.base_range.name
            assert data["base_range"]["base_range"] is None
            assert "base" not in data["base_range"]

    def test_circular_reference_does_not_crash(self):
        """
        Проверка преобразования циклической ссылки на сущность в идентификатор и имя.
        """
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
        """
        Проверка исключения при передаче простого значения ссылочному конвертору.
        """
        # Подготовка
        conv = reference_convertor()

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            conv.convert("bad", "не сущность")
        with pytest.raises(arguments_exception):
            conv.convert("не сущность")

    def test_nested_datetime_and_primitives(self):
        """
        Проверка преобразования дат и простых значений во вложенных коллекциях объекта.
        """
        # Подготовка
        source = SimpleNamespace(items=[1, True, None, {"date": datetime(2026, 11, 5)}])

        # Действие
        result = reference_convertor().convert(source)

        # Проверка
        assert result == {
            "items": [1, True, None, {"date": "2026-11-05T00:00:00"}]
        }


@pytest.mark.parametrize("value", [True, False])
def test_basic_boolean_single_argument(value):
    """
    Проверка преобразования логического значения без указания имени поля.
    """
    # Подготовка
    converter = basic_convertor()

    # Действие
    result = converter.convert(value)

    # Проверка
    assert result == {"value": value}


def test_datetime_preserves_timezone_and_microseconds():
    """
    Проверка сохранения часового пояса и микросекунд при преобразовании даты.
    """
    # Подготовка
    value = datetime(2026, 11, 5, 12, 30, 15, 123456, timezone(timedelta(hours=8)))

    # Действие
    result = datetime_convertor().convert("at", value)

    # Проверка
    assert result == {
        "at": "2026-11-05T12:30:15.123456+08:00"
    }
