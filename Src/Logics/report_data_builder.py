from enum import Enum

from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Dtos.report_data_dto import report_data_dto
from Src.Dtos.report_field_dto import report_field_dto
from Src.Dtos.report_table_dto import report_table_dto


class report_data_builder:
    """Получает свойства и все коллекции модели рефлексией, без реестра сущностей."""

    @staticmethod
    def _properties(source: abstract_entity) -> dict[str, object]:
        """Прочитать публичные свойства, исключив служебную метку типа."""
        names = {
            name
            for cls in type(source).__mro__
            for name, attribute in vars(cls).items()
            if isinstance(attribute, property) and not name.startswith("_") and name != "type"
        }
        return {
            name: getattr(source, name)
            for name in sorted(names, key=lambda name: (name not in ("id", "name"), name))
        }

    @staticmethod
    def _is_collection(value: object) -> bool:
        """Определить значения, образующие табличные части."""
        return isinstance(value, (list, tuple, dict))

    @classmethod
    def _text(cls, value: object) -> str:
        """Представить ссылку именем и кодом; пустое значение оставить пустым."""
        if value is None:
            return ""
        if isinstance(value, abstract_entity):
            return f"{value.name} ({value.id})"
        if isinstance(value, Enum):
            return str(value.value)
        if cls._is_collection(value):
            return f"[{len(value)}]"
        return str(value)

    def build(self, source: abstract_entity) -> report_data_dto:
        """Собрать представление модели; повторы ссылок раскрывать до границы цикла."""
        if not isinstance(source, abstract_entity):
            raise arguments_exception("Источник отчёта должен быть доменной моделью", "source")
        properties = self._properties(source)
        result = report_data_dto(
            title=type(source).__name__,
            fields=[
                report_field_dto(name, self._text(value))
                for name, value in properties.items()
                if not self._is_collection(value)
            ],
        )
        self._collect_tables(source, "", frozenset(), result.tables)
        return result

    def _collect_tables(self, value: object, path: str, ancestors: frozenset[int], tables: list[report_table_dto]) -> None:
        """Рекурсивно собрать все коллекции, включая вложенные агрегаты и словари."""
        if not isinstance(value, abstract_entity) and not self._is_collection(value):
            return
        token = id(value)
        if token in ancestors:
            return
        ancestors = ancestors | {token}
        if isinstance(value, abstract_entity):
            properties = self._properties(value)
            # У вложенного агрегата сохраняются и его собственные поля, а не только строки.
            if path and any(self._is_collection(item) for item in properties.values()):
                fields = [
                    report_field_dto(name, self._text(item))
                    for name, item in properties.items() if not self._is_collection(item)
                ]
                tables.append(report_table_dto(path, [field.name for field in fields], [[field.value for field in fields]]))
            for name, item in properties.items():
                child_path = f"{path}.{name}" if path else name
                self._collect_tables(item, child_path, ancestors, tables)
            return

        entries = list(value.items()) if isinstance(value, dict) else list(enumerate(value))
        records = []
        columns = []
        for key, item in entries:
            record = {"key": str(key)} if isinstance(value, dict) else {}
            if isinstance(item, abstract_entity):
                record.update({name: self._text(field) for name, field in self._properties(item).items()})
            else:
                record["value"] = self._text(item)
            records.append(record)
            for name in record:
                if name not in columns:
                    columns.append(name)
        tables.append(report_table_dto(path, columns, [[record.get(name, "") for name in columns] for record in records]))
        for key, item in entries:
            self._collect_tables(item, f"{path}[{key}]", ancestors, tables)
