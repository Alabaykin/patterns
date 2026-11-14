from collections.abc import Mapping

from Src.Core.abstract_entity import abstract_entity
from Src.Core.exception import arguments_exception
from Src.Logics.entity_types import entity_links


class reference_index:
    """Прямые и обратные ссылки между кодами корневых сущностей."""

    def __init__(self):
        """Создать пустые индексы без ссылок на сами доменные объекты."""
        self.__forward: dict[str, set[str]] = {}
        self.__reverse: dict[str, set[str]] = {}

    @staticmethod
    def _dependencies(source: abstract_entity, known: Mapping[str, abstract_entity], existing=None) -> set[str]:
        """Проверить прямые ссылки модели и её строк по индексу хранилища."""
        result = set()
        for owner, field in entity_links(source):
            value = getattr(owner, field)
            if value is not None:
                if known.get(value.id) is not value:
                    raise arguments_exception(f"Ссылка на отсутствующую сущность '{value.id}'", "id")
                result.add(source.id if value is existing else value.id)
        return result

    def rebuild(self, known: Mapping[str, abstract_entity]) -> None:
        """Построить индекс после загрузки и проверить циклы за один обход графа."""
        forward = {key: self._dependencies(item, known) for key, item in known.items()}
        reverse = {}
        for owner, targets in forward.items():
            for target in targets:
                reverse.setdefault(target, set()).add(owner)
        remaining = {key: len(targets) for key, targets in forward.items()}
        ready = [key for key, count in remaining.items() if count == 0]
        processed = 0
        while ready:
            target = ready.pop()
            processed += 1
            for owner in reverse.get(target, ()):
                remaining[owner] -= 1
                if remaining[owner] == 0:
                    ready.append(owner)
        if processed != len(forward):
            raise arguments_exception("Циклическая ссылка между сущностями", "id")
        self.__forward = forward
        self.__reverse = reverse

    def prepare(self, source: abstract_entity, known: Mapping[str, abstract_entity], existing=None) -> set[str]:
        """Проверить связи кандидата и достижимость цикла по индексу, не меняя его."""
        targets = self._dependencies(source, known, existing)
        pending = list(targets)
        visited = set()
        while pending:
            target = pending.pop()
            if target == source.id:
                raise arguments_exception("Циклическая ссылка между сущностями", "id")
            if target not in visited:
                visited.add(target)
                pending.extend(self.__forward.get(target, ()))
        return targets

    def referrers(self, identifier: str) -> list[str]:
        """Найти прямых и транзитивных пользователей по обратному индексу без рефлексии."""
        result = set()
        pending = list(self.__reverse.get(identifier, ()))
        while pending:
            owner = pending.pop()
            if owner not in result:
                result.add(owner)
                pending.extend(self.__reverse.get(owner, ()))
        result.discard(identifier)
        return sorted(result)

    def _remove_outgoing(self, identifier: str) -> None:
        """Удалить только исходящие рёбра, сохранив входящие ссылки при обновлении."""
        for target in self.__forward.pop(identifier, ()):
            owners = self.__reverse[target]
            owners.discard(identifier)
            if not owners:
                del self.__reverse[target]

    def update(self, identifier: str, targets: set[str], old_identifier: str | None = None) -> None:
        """Обновить только рёбра изменённого объекта после успешной записи в кэш."""
        if old_identifier is not None and old_identifier != identifier:
            self.remove(old_identifier)
        self._remove_outgoing(identifier)
        self.__forward[identifier] = set(targets)
        for target in targets:
            self.__reverse.setdefault(target, set()).add(identifier)

    def remove(self, identifier: str) -> None:
        """Удалить рёбра свободной сущности после её удаления из кэша."""
        self._remove_outgoing(identifier)
        self.__reverse.pop(identifier, None)
