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
        +organization() organization_model
        +company() organization_model
        +boss_name() str
        +account_name() str
        +is_first() bool
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

    abstract_manager <|-- settings_manager : Наследование
    abstract_manager <|-- storage_manager : Наследование

    settings_manager o-- settings_model : Управляет
    settings_model *-- organization_model : Содержит

    storage_manager o-- range_model : Хранит уникальные
    storage_manager o-- group_model : Хранит уникальные
    storage_manager o-- warehouse_model : Хранит уникальные
    storage_manager o-- nomenclature_model : Хранит уникальные

    nomenclature_model --> group_model : Относится к
    nomenclature_model --> range_model : Единица измерения
    range_model o-- range_model : Базовая единица
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
    Note over SM: В памяти (кэше) создаются эталонные:<br/>ranges, groups, warehouses, nomenclatures
    SM-->>Client: is_loaded = True
```
