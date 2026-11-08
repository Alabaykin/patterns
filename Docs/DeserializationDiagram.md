# Диаграмма классов десериализации JSON

```mermaid
classDiagram
    direction TB

    class storage_manager {
        +load(file_name) None
        -_deserialize_collections(data) dict
    }
    class abstract_deserialize_factory {
        <<abstract>>
        +create(type_name) abstract_deserializer
        +deserialize(data) object
    }
    class deserialize_factory {
        -__model_types
        +create(type_name) abstract_deserializer
        +deserialize(data) object
    }
    class abstract_deserializer {
        <<abstract>>
        +model_type
        +deserialize(data) abstract_entity
    }
    class domain_deserializer {
        -__factory
        +deserialize(data) abstract_entity
    }
    class abstract_entity {
        <<abstract>>
        +id str
        +name str
        +type str
        +from_dict(data) abstract_entity
        #_create_from_fields(fields) abstract_entity
    }
    class nomenclature_model {
        #_create_from_fields(fields) nomenclature_model
    }
    class organization_model {
        #_create_from_fields(fields) organization_model
    }
    class recipe_model {
        #_create_from_fields(fields) recipe_model
        +add_row(row) None
    }
    class recipe_row_model {
        #_create_from_fields(fields) recipe_row_model
    }

    abstract_deserialize_factory <|-- deserialize_factory
    abstract_deserializer <|-- domain_deserializer
    storage_manager ..> deserialize_factory 
    deserialize_factory ..> domain_deserializer
    domain_deserializer --> abstract_deserialize_factory
    domain_deserializer ..> abstract_entity : передаёт восстановленные поля в from_dict
    abstract_entity <|-- nomenclature_model
    abstract_entity <|-- organization_model
    abstract_entity <|-- recipe_model
    abstract_entity <|-- recipe_row_model
```
