from abc import ABC, abstractmethod
from urllib.parse import quote

from flask import Response
from werkzeug.utils import secure_filename

from Src.Core.abstract_entity import abstract_entity
from Src.Dtos.report_result_dto import report_result_dto


class abstract_report(ABC):
    """Контракт построителя отчёта и единая выдача результата через HTTP."""

    @property
    @abstractmethod
    def mimetype(self) -> str:
        """MIME-тип формата."""
        pass

    @property
    def is_attachment(self) -> bool:
        """Признак выдачи файла вместо отображения текста."""
        return False

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Расширение файла отчёта."""
        pass

    @abstractmethod
    def build(self, source: abstract_entity) -> report_result_dto:
        """Сформировать отчёт по доменной модели."""
        pass

    def create_response(self, result: report_result_dto, filename_prefix: str = "report") -> Response:
        """Сформировать ответ с MIME-типом и корректным именем скачиваемого файла."""
        data = bytes(result.binary) if self.is_attachment else result.text
        headers = {}
        if self.is_attachment:
            safe_name = secure_filename(filename_prefix) or "report"
            encoded_name = quote(filename_prefix.replace(" ", "_"), safe="")
            headers["Content-Disposition"] = (
                f'attachment; filename="{safe_name}.{self.file_extension}"; '
                f"filename*=UTF-8''{encoded_name}.{self.file_extension}"
            )
        return Response(data, mimetype=self.mimetype, headers=headers)
