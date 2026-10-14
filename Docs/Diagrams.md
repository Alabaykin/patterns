# UML диаграммы классов для `settings_manager` и `storage_manager`

Ниже представлены UML-диаграммы классов, отражающие структуру менеджеров, применение паттерна **Singleton**, отношение наследования от `abstract_manager`, а также связи с доменными моделями.

---

## 1. UML диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_manager {
        <<Abstract>>
        -__file_name: str
        -__is_loaded: bool
        -__data: list | dict
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
    }

    class settings_manager {
        <<Singleton>>
        -instance: settings_manager$
        -__default_file_name: str
        -_settings: settings_model
        -__is_loaded: bool
        -__data: dict
        +__new__(cls) settings_manager$
        +load(file_name: str) void
        +convert() bool
        +is_loaded() bool
        +settings() settings_model
    }

    class storage_manager {
        <<Singleton>>
        -instance: storage_manager$
        -_ranges: dict~str, range_model~
        -_groups: dict~str, group_model~
        -_warehouses: dict~str, warehouse_model~
        -_nomenclatures: dict~str, nomenclature_model~
        -_is_loaded: bool
        +__new__(cls) storage_manager$
        +ranges() list~range_model~
        +groups() list~group_model~
        +warehouses() list~warehouse_model~
        +nomenclatures() list~nomenclature_model~
        +add_range(item: range_model) void
        +add_group(item: group_model) void
        +add_warehouse(item: warehouse_model) void
        +add_nomenclature(item: nomenclature_model) void
        +data() dict
        -__generate_default_data() void
        +load(file_name: str) void
        +convert(settings: settings_model) bool
        +is_loaded() bool
    }

    class settings_model {
        -__organization: organization_model
        -__boss_name: str
        -__account_name: str
        -__is_first: bool
        -__response_format: str
        +organization() organization_model
        +company() organization_model
        +boss_name() str
        +account_name() str
        +is_first() bool
        +response_format() str
    }


    class organization_model {
        -_name: str
        -_inn: str
        -_bik: str
        -_account: str
        -_ownership_type: str
        +inn() str
        +bik() str
        +account() str
        +ownership_type() str
    }

    class range_model {
        -_name: str
        -_coefficient: float
        -_base_range: range_model
        +coefficient() float
        +base_range() range_model
        +to_base(value: float) float
        +convert_to(target: range_model, value: float) float
    }

    class group_model {
        -_name: str
    }

    class warehouse_model {
        -_name: str
    }

    class nomenclature_model {
        -_name: str
        -_full_name: str
        -_group: group_model
        -_range: range_model
        +full_name() str
        +group() group_model
        +range() range_model
    }

    class abstract_entity {
        <<Abstract>>
        -_id: str
        -_name: str
        +id() str
        +name() str
    }

    class recipe_row_model {
        -_nomenclature: nomenclature_model
        -_range: range_model
        -_gross: float
        -_net: float
        -_sub_recipe: recipe_model
        +nomenclature() nomenclature_model
        +range() range_model
        +gross() float
        +net() float
        +sub_recipe() recipe_model
        +create(nomenclature, range, gross, net)$ recipe_row_model
    }

    class recipe_model {
        -_rows: list~recipe_row_model~
        -_steps: str
        -_output_range: range_model
        -_target_nomenclature: nomenclature_model
        +rows() list~recipe_row_model~
        +steps() str
        +output_range() range_model
        +target_nomenclature() nomenclature_model
        +add_row(row: recipe_row_model) void
        +remove_row(row_or_name) bool
        +calculate_gross(target_range: range_model) float
        +calculate_net(target_range: range_model) float
        +create(name, rows, steps, output_range, target_nomenclature)$ recipe_model
    }

    abstract_manager <|-- settings_manager : Наследование
    abstract_manager <|-- storage_manager : Наследование

    abstract_entity <|-- group_model : Наследование
    abstract_entity <|-- warehouse_model : Наследование
    abstract_entity <|-- range_model : Наследование
    abstract_entity <|-- nomenclature_model : Наследование
    abstract_entity <|-- recipe_row_model : Наследование
    abstract_entity <|-- recipe_model : Наследование

    settings_manager o-- settings_model : Управляет
    settings_model *-- organization_model : Содержит

    storage_manager o-- range_model : Хранит уникальные
    storage_manager o-- group_model : Хранит уникальные
    storage_manager o-- warehouse_model : Хранит уникальные
    storage_manager o-- nomenclature_model : Хранит уникальные
    storage_manager o-- recipe_model : Хранит уникальные

    nomenclature_model --> group_model : Относится к
    nomenclature_model --> range_model : Единица измерения
    range_model o-- range_model : Базовая единица

    recipe_model *-- recipe_row_model : Содержит строки
    recipe_model --> range_model : Выходная единица
    recipe_model --> nomenclature_model : Целевая номенклатура
    recipe_row_model --> nomenclature_model : Ингредиент
    recipe_row_model --> range_model : Единица измерения
    recipe_row_model o--> recipe_model : Вложенный рецепт (sub_recipe)
```

---

## 2. Диаграмма взаимодействия при первом старте (First Start)

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant SM as storage_manager (Singleton)
    participant StM as settings_manager (Singleton)

    Client->>SM: storage_manager()
    Note over SM: Возвращает единственный экземпляр (__new__)
    Client->>SM: load()
    SM->>StM: settings_manager().settings.is_first
    StM-->>SM: True (первый старт)
    SM->>SM: __generate_default_data()
    Note over SM: В памяти (кэше) создаются через фабричные методы:<br/>ranges, groups, warehouses, nomenclatures, recipes
    SM-->>Client: is_loaded = True
```

---

## 3. UML диаграмма классов для моделей рецептов (DDD)

```mermaid
classDiagram
    direction TB

    class abstract_entity {
        <<Abstract>>
        -_id: str
        -_name: str
        +id() str
        +name() str
    }

    class recipe_model {
        -_name: str
        -_rows: list~recipe_row_model~
        -_steps: str
        -_output_range: range_model
        -_target_nomenclature: nomenclature_model
        +name() str
        +rows() list~recipe_row_model~
        +steps() str
        +output_range() range_model
        +target_nomenclature() nomenclature_model
        +add_row(row: recipe_row_model) void
        +remove_row(row_or_name) bool
        +calculate_gross(target_range: range_model) float
        +calculate_net(target_range: range_model) float
        +create_dough_recipe()$ recipe_model
        +create_cream_recipe()$ recipe_model
        +create_waffle_cake_recipe()$ recipe_model
    }

    class recipe_row_model {
        -_nomenclature: nomenclature_model
        -_range: range_model
        -_gross: float
        -_net: float
        -_sub_recipe: recipe_model
        +nomenclature() nomenclature_model
        +range() range_model
        +gross() float
        +net() float
        +sub_recipe() recipe_model
        +create_flour_row(gross, net)$ recipe_row_model
        +create_sugar_row(gross, net)$ recipe_row_model
        +create_butter_row(gross, net)$ recipe_row_model
        +create_egg_row(gross, net)$ recipe_row_model
        +create_vanilla_row(gross, net)$ recipe_row_model
        +create_condensed_milk_row(gross, net)$ recipe_row_model
        +create_dough_row(gross, net)$ recipe_row_model
        +create_cream_row(gross, net)$ recipe_row_model
        +create_box_row(gross, net)$ recipe_row_model
    }

    class nomenclature_model {
        -_name: str
        -_full_name: str
        -_group: group_model
        -_range: range_model
        +create_flour()$ nomenclature_model
        +create_sugar()$ nomenclature_model
        +create_butter()$ nomenclature_model
        +create_egg()$ nomenclature_model
        +create_vanilla()$ nomenclature_model
        +create_condensed_milk()$ nomenclature_model
        +create_shortcrust_dough()$ nomenclature_model
        +create_cream()$ nomenclature_model
        +create_waffle_cake()$ nomenclature_model
        +create_cake_box()$ nomenclature_model
    }

    class range_model {
        -_name: str
        -_coefficient: float
        -_base_range: range_model
        +create_gramm()$ range_model
        +create_kilogramm()$ range_model
        +create_piece()$ range_model
        +create_milliliter()$ range_model
        +create_liter()$ range_model
        +convert_to(target, value) float
    }

    class group_model {
        -_name: str
        +create_raw()$ group_model
        +create_semi()$ group_model
        +create_dishes()$ group_model
        +create_package()$ group_model
    }

    class warehouse_model {
        -_name: str
        +create_main()$ warehouse_model
        +create_kitchen()$ warehouse_model
        +create_delivery()$ warehouse_model
    }

    abstract_entity <|-- recipe_model : Наследование
    abstract_entity <|-- recipe_row_model : Наследование
    abstract_entity <|-- nomenclature_model : Наследование
    abstract_entity <|-- range_model : Наследование
    abstract_entity <|-- group_model : Наследование
    abstract_entity <|-- warehouse_model : Наследование

    recipe_model "1" *-- "*" recipe_row_model : Rows (Спецификация)
    recipe_model o--> "0..1" nomenclature_model : Target Dish / Semi
    recipe_model o--> "0..1" range_model : Output Range
    recipe_row_model o--> "1" nomenclature_model : Ingredient / Semi / Package
    recipe_row_model o--> "1" range_model : Unit Range
    recipe_row_model o--> "0..1" recipe_model : Sub-Recipe (Вложенный рецепт)
```

---

## 4. UML диаграмма классов для Фабрики отчётов (Factory Method)

```mermaid
classDiagram
    direction TB

    class abstract_report {
        <<Abstract>>
        +build(source)* report_result_dto
    }

    class abstract_report_factory {
        <<Abstract>>
        +create(report_type: report_type_enum)* abstract_report
        +create_default()* abstract_report
    }

    class report_factory {
        -__mapping: dict~report_type_enum, type[abstract_report]~
        -__settings: settings_model
        +settings() settings_model
        +create(report_type: report_type_enum) abstract_report
        +create_default() abstract_report
    }

    class text_report {
        -__recipe: recipe_model
        +build(source) report_result_dto
    }

    class markdown_report {
        +build(source) report_result_dto
    }

    class csv_report {
        +build(source) report_result_dto
    }

    class xml_report {
        +build(source) report_result_dto
    }

    class html_report {
        +build(source) report_result_dto
    }

    class report_type_enum {
        <<Enumeration>>
        TXT
        MARKDOWN
        CSV
        XML
        HTML
        +from_string(value: str)$ report_type_enum
    }

    class report_result_dto {
        -__text: str
        -__binary: list
        +text() str
        +binary() list
    }

    class abstract_entity {
        <<Abstract>>
        -_id: str
        -_name: str
    }

    abstract_report_factory <|-- report_factory : Реализация
    abstract_report <|-- text_report : Реализация
    abstract_report <|-- markdown_report : Реализация
    abstract_report <|-- csv_report : Реализация
    abstract_report <|-- xml_report : Реализация
    abstract_report <|-- html_report : Реализация

    abstract_entity <|-- report_result_dto : Наследование

    report_factory ..> abstract_report : Создает
    report_factory ..> report_type_enum : Использует
    report_factory o--> settings_model : Инкапсулирует

    abstract_report ..> report_result_dto : Возвращает
```


