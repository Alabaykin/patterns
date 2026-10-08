from __future__ import annotations
from Src.Core.abstract_entity import abstract_entity
from Src.Core.validator import validator
from Src.Core.exception import arguments_exception, operation_exception
from Src.Models.recipe_row_model import recipe_row_model
from Src.Models.nomenclature_model import nomenclature_model
from Src.Models.range_model import range_model


class recipe_model(abstract_entity):
    """
    Модель рецепта (технологической карты).
    Содержит спецификацию ингредиентов (сырье, полуфабрикаты, упаковка),
    пошаговую инструкцию приготовления и методы расчета веса Брутто и Нетто.
    """
    _rows: list[recipe_row_model] = None
    _steps: str = ""
    _output_range: range_model = None
    _target_nomenclature: nomenclature_model = None

    def __init__(
        self,
        name: str,
        rows: list[recipe_row_model] = None,
        steps: str = "",
        output_range: range_model = None,
        target_nomenclature: nomenclature_model = None
    ):
        """
        Инициализация рецепта.
        :param name: Наименование рецепта.
        :param rows: Список строк рецепта (ингредиентов).
        :param steps: Пошаговая инструкция приготовления.
        :param output_range: Единица измерения готового изделия/полуфабриката.
        :param target_nomenclature: Номенклатура готового изделия/полуфабриката.
        """
        self.name = name
        self._rows = []
        if rows:
            for r in rows:
                self.add_row(r)
        self.steps = steps
        self.output_range = output_range
        self.target_nomenclature = target_nomenclature

    @property
    def rows(self) -> list[recipe_row_model]:
        """
        Список строк рецепта (ингредиентов).
        """
        return list(self._rows)

    @property
    def steps(self) -> str:
        """
        Пошаговое описание технологического процесса.
        """
        return self._steps

    @steps.setter
    def steps(self, value: str) -> None:
        if value is None:
            self._steps = ""
        elif not isinstance(value, str):
            raise arguments_exception("Описание этапов приготовления должно быть строкой", "steps")
        else:
            self._steps = value.strip()

    @property
    def output_range(self) -> range_model | None:
        """
        Единица измерения выхода рецепта.
        """
        return self._output_range

    @output_range.setter
    def output_range(self, value: range_model | None) -> None:
        if value is not None:
            validator.validate(value, range_model)
        self._output_range = value

    @property
    def target_nomenclature(self) -> nomenclature_model | None:
        """
        Целевая номенклатура готового блюда / полуфабриката.
        """
        return self._target_nomenclature

    @target_nomenclature.setter
    def target_nomenclature(self, value: nomenclature_model | None) -> None:
        if value is not None:
            validator.validate(value, nomenclature_model)
        self._target_nomenclature = value

    def add_row(self, row: recipe_row_model) -> None:
        """
        Добавить строку (ингредиент) в рецепт.
        """
        validator.validate(row, recipe_row_model)
        self._rows.append(row)

    def remove_row(self, row_or_name: recipe_row_model | str) -> bool:
        """
        Исключить строку из рецепта по объекту строки или по имени ингредиента / id.
        """
        if isinstance(row_or_name, recipe_row_model):
            if row_or_name in self._rows:
                self._rows.remove(row_or_name)
                return True
            return False
        elif isinstance(row_or_name, str):
            target_name = row_or_name.strip().lower()
            for r in self._rows:
                if (
                    r.id == row_or_name
                    or r.nomenclature.name.strip().lower() == target_name
                    or r.nomenclature.full_name.strip().lower() == target_name
                ):
                    self._rows.remove(r)
                    return True
            return False
        else:
            raise arguments_exception("Параметр должен быть объектом recipe_row_model или строкой", "row_or_name")

    def calculate_gross(self, target_range: range_model = None) -> float:
        """
        Вычисление общего веса/количества Брутто путем сложения веса каждого ингредиента.
        """
        total = 0.0
        target = target_range or self._output_range

        for row in self._rows:
            val = row.gross
            if target is not None:
                try:
                    val = row.range.convert_to(target, val)
                except Exception:
                    # Если единицы несовместимы (например, штуки и кг), добавляем без пересчета
                    pass
            total += val

        return round(total, 4)

    def calculate_net(self, target_range: range_model = None) -> float:
        """
        Вычисление общего веса Нетто путем сложения веса каждого ингредиента.
        """
        total = 0.0
        target = target_range or self._output_range

        for row in self._rows:
            val = row.net
            if target is not None:
                try:
                    val = row.range.convert_to(target, val)
                except Exception:
                    pass
            total += val

        return round(total, 4)


    @staticmethod
    def create_dough_recipe() -> recipe_model:
        """
        Фабричный метод создания рецепта полуфабриката 'Песочное тесто'.
        """
        rows = [
            recipe_row_model.create_flour_row(0.250, 0.250),
            recipe_row_model.create_butter_row(0.100, 0.100),
            recipe_row_model.create_sugar_row(0.150, 0.150),
            recipe_row_model.create_egg_row(2.0, 2.0),
            recipe_row_model.create_vanilla_row(2.0, 2.0),
        ]
        steps = (
            "1. Муку просеять через сито.\n"
            "2. Сливочное масло растереть с сахаром и ванилином.\n"
            "3. Добавить куриные яйца, перемешать миксером.\n"
            "4. Ввести муку и замесить тесто, охладить 30 минут."
        )
        return recipe_model(
            name="Песочное тесто",
            rows=rows,
            steps=steps,
            output_range=range_model.create_kilogramm(),
            target_nomenclature=nomenclature_model.create_shortcrust_dough()
        )

    @staticmethod
    def create_cream_recipe() -> recipe_model:
        """
        Фабричный метод создания рецепта полуфабриката 'Крем со сгущенкой'.
        """
        rows = [
            recipe_row_model.create_butter_row(0.100, 0.100),
            recipe_row_model.create_condensed_milk_row(0.200, 0.200),
        ]
        steps = (
            "1. Взбить размягченное сливочное масло до пышности.\n"
            "2. Порциями ввести вареное сгущенное молоко до однородной массы."
        )
        return recipe_model(
            name="Крем со сгущенкой",
            rows=rows,
            steps=steps,
            output_range=range_model.create_kilogramm(),
            target_nomenclature=nomenclature_model.create_cream()
        )

    @staticmethod
    def create_waffle_cake_recipe() -> recipe_model:
        """
        Фабричный метод создания рецепта готового блюда с полуфабрикатами и упаковкой
        'Вафельный торт с кремом'.
        """
        rows = [
            recipe_row_model.create_dough_row(0.550, 0.550),
            recipe_row_model.create_cream_row(0.300, 0.300),
            recipe_row_model.create_box_row(1.0, 1.0),
        ]
        steps = (
            "1. Выпечь коржи из теста при 190°C.\n"
            "2. Промазать коржи кремом со сгущенкой.\n"
            "3. Обсыпать торт крошкой.\n"
            "4. Упаковать торт в коробку для транспортировки."
        )
        return recipe_model(
            name="Вафельный торт с кремом",
            rows=rows,
            steps=steps,
            output_range=range_model.create_piece(),
            target_nomenclature=nomenclature_model.create_waffle_cake()
        )