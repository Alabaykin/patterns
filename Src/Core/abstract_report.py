from abc import ABC, abstractmethod
from urllib.parse import quote
from flask import Response
from Src.Dtos.report_result_dto import report_result_dto
from Src.Core.exception import arguments_exception


class abstract_report(ABC):
    """
    Базовый абстрактный класс формирования отчетов.
    Задает единый контракт генерации отчетов (Template Method)
    и полиморфного формирования HTTP-ответов.
    """

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """
        MIME-тип представления отчета
        """
        pass

    @property
    def mime_type(self) -> str:
        """
        Псевдоним для MIME-типа представления отчета
        """
        return self.mimetype

    @property
    def is_attachment(self) -> bool:
        """
        Признак передачи отчета в виде скачиваемого вложения
        """
        return False

    @property
    def is_binary(self) -> bool:
        """
        Флаг формата результата: True -> binary, False -> text (псевдоним is_attachment)
        """
        return self.is_attachment

    @property
    def file_extension(self) -> str:
        """
        Расширение файла отчета
        """
        return "txt"

    @property
    def extension(self) -> str:
        """
        Псевдоним для расширения файла отчета
        """
        return self.file_extension

    def create_response(self, result: report_result_dto, filename_prefix: str = "report"):
        """
        Полиморфное построение HTTP-ответа без процедурных ветвлений.
        """
        data = bytes(result.binary) if self.is_attachment else result.text
        headers = {}
        if self.is_attachment:
            safe_name = filename_prefix.replace(" ", "_")
            encoded_name = quote(safe_name)
            headers["Content-Disposition"] = (
                f'attachment; filename="{safe_name}.{self.file_extension}"; '
                f"filename*=UTF-8''{encoded_name}.{self.file_extension}"
            )

        content_type = self.mimetype
        if not self.is_attachment and "charset" not in content_type:
            content_type = f"{content_type}; charset=utf-8"

        return Response(data, mimetype=content_type, headers=headers)


    def _resolve_handler(self, source):
        """
        Точка расширения для динамического разрешения специализированного обработчика.
        По умолчанию возвращает текущий экземпляр (self).
        """
        return self

    def build_header(self, source) -> str:
        """
        Сформировать заголовок отчета (шаг шаблонного метода).
        """
        return ""

    def build_body(self, source) -> str:
        """
        Сформировать тело отчета (шаг шаблонного метода).
        """
        return ""

    def build_footer(self, source) -> str:
        """
        Сформировать подвал отчета (шаг шаблонного метода).
        """
        return ""

    def _combine(self, header: str, body: str, footer: str) -> str:
        """
        Объединение шагов отчета в итоговый контент.
        """
        parts = [p for p in (header, body, footer) if p]
        return "\n".join(parts)

    def build(self, source) -> report_result_dto:
        """
        Шаблонный метод (Template Method) формирования отчета.
        Последовательно выполняет:
        1. Валидацию источника данных.
        2. Разрешение обработчика (если вызван базовый класс формата).
        3. Формирование заголовка (build_header).
        4. Формирование тела (build_body).
        5. Формирование подвала (build_footer).
        6. Объединение частей (_combine).
        7. Упаковку в report_result_dto (бинарные байты при is_attachment или текст).
        """
        if source is None:
            raise arguments_exception("Источник данных не может быть пустым!")

        handler = self._resolve_handler(source)
        if handler is not self:
            return handler.build(source)

        header = self.build_header(source)
        body = self.build_body(source)
        footer = self.build_footer(source)

        content = self._combine(header, body, footer)

        result = report_result_dto()
        if self.is_attachment:
            result.binary = list(content.encode("utf-8"))
        else:
            result.text = content
        return result

