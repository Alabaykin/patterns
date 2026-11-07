from datetime import datetime
from types import SimpleNamespace
import pytest
from Src.Core.abstract_convert_factory import abstract_convert_factory
from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.convert_factory import convert_factory
from Src.Logics.basic_convertor import basic_convertor
from Src.Logics.datetime_convertor import datetime_convertor
from Src.Logics.reference_convertor import reference_convertor
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
            """
            Вспомогательный тип без зарегистрированного конвертора.
            """
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

    def test_arbitrary_object_preserves_public_fields(self):
        """
        Проверка сохранения публичных полей обычного объекта при преобразовании.
        """
        # Подготовка
        source = SimpleNamespace(title="Заказ", rows=[{"date": datetime(2026, 11, 5)}])
        expected = {"title": "Заказ", "rows": [{"date": "2026-11-05T00:00:00"}]}
        factory = convert_factory()

        # Действие
        result = factory.convert(source)
        named_result = factory.convert("order", source)

        # Проверка
        assert result == expected
        assert named_result == {"order": expected}

    def test_slots_and_inherited_properties(self):
        """
        Проверка преобразования slots и унаследованных свойств объекта.
        """
        # Подготовка
        class Parent:
            """
            Базовый класс с публичным свойством для проверки наследования.
            """
            __slots__ = ()

            @property
            def title(self):
                """
                Получение наименования тестового объекта.
                """
                return "Заказ"

        class Order(Parent):
            """
            Тестовый объект с публичным, закрытым и неинициализированным slots.
            """
            __slots__ = ("quantity", "_secret", "uninitialized")

        source = Order()
        source.quantity = 3
        source._secret = "hidden"

        # Действие
        result = convert_factory().convert(source)

        # Проверка
        assert result == {"quantity": 3, "title": "Заказ"}

    @pytest.mark.parametrize("source", [complex(1, 2), b"bytes", object()])
    def test_unsupported_values_raise_at_any_depth(self, source):
        """
        Проверка исключения для неподдерживаемых значений на разных уровнях вложенности.
        """
        # Подготовка
        factory = convert_factory()
        values = (source, [source], {"nested": source})

        # Действие и Проверка
        for value in values:
            with pytest.raises(arguments_exception):
                factory.serialize(value)
            with pytest.raises(arguments_exception):
                factory.convert("field", value)

    @pytest.mark.parametrize("kind", ["list", "dict", "object"])
    def test_cycles_raise_clear_error(self, kind):
        """
        Проверка исключения при циклических ссылках коллекций и обычных объектов.
        """
        # Подготовка
        if kind == "list":
            source = []
            source.append(source)
        elif kind == "dict":
            source = {}
            source["self"] = source
        else:
            source = SimpleNamespace()
            source.self = source

        # Действие и Проверка
        with pytest.raises(arguments_exception, match="Циклическая"):
            convert_factory().serialize(source)

    def test_shared_reference_is_serialized_in_each_branch(self):
        """
        Проверка полного преобразования общей ссылки в независимых ветвях структуры.
        """
        # Подготовка
        item = range_model.create_piece()

        # Действие
        data = convert_factory().serialize([item, item])

        # Проверка
        assert data[0] == data[1]
        assert "coefficient" in data[1]

    def test_distinct_entities_with_same_id_keep_their_fields(self):
        """
        Проверка сохранения полей разных сущностей с одинаковым идентификатором.
        """
        # Подготовка
        first = range_model.create_piece()
        second = range_model.create_gramm()
        second.id = first.id
        first.base_range = second

        # Действие
        result = convert_factory().serialize(first)

        # Проверка
        assert result["base_range"]["coefficient"] == second.coefficient

    def test_nested_values_use_registered_converters(self):
        """
        Проверка использования зарегистрированного конвертора для вложенных значений.
        """
        # Подготовка
        class CustomInt(basic_convertor):
            """
            Тестовый конвертор целых чисел со смещением значения.
            """
            def serialize_value(self, value, stack=None):
                """
                Преобразование целого числа с добавлением тестового смещения.
                """
                return value + 10

        factory = convert_factory()
        factory.converters[int] = CustomInt
        source = SimpleNamespace(items=[1, {"count": 2}])

        # Действие
        result = factory.serialize(source)

        # Проверка
        assert result == {
            "items": [11, {"count": 12}]
        }

    def test_getter_error_is_not_silently_ignored(self):
        """
        Проверка передачи ошибки чтения свойства вызывающему коду.
        """
        # Подготовка
        class Broken:
            """
            Тестовый объект со свойством, вызывающим исключение.
            """
            @property
            def field(self):
                """
                Получение свойства с ошибкой для проверки передачи исключения.
                """
                raise RuntimeError("getter failed")

        source = Broken()

        # Действие и Проверка
        with pytest.raises(RuntimeError, match="getter failed"):
            convert_factory().serialize(source)

    def test_dictionary_key_collision_raises(self):
        """
        Проверка исключения при совпадении ключей после преобразования в строки.
        """
        # Подготовка
        source = {1: "one", "1": "another"}

        # Действие и Проверка
        with pytest.raises(arguments_exception):
            convert_factory().serialize(source)
