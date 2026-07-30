"""Log handler abstractions for the RKGB Logging & Observability Framework.

Handlers wrap Python's standard ``logging.Handler`` classes and apply
structlog ``ProcessorFormatter`` so that structured output is produced by
every sink.

Implemented handlers:
    * :class:`ConsoleLogHandler` — stdout output (always available)
    * :class:`FileLogHandler` — plain-text file output
    * :class:`JSONFileLogHandler` — JSON-formatted file output
    * :class:`RotatingFileLogHandler` — size-based rotating file output

Future handlers (not implemented here — only the pattern is established):
    * ``KafkaLogHandler`` — publish log records to a Kafka topic
    * ``ElasticsearchLogHandler`` — ship to Elastic
    * ``LokiLogHandler`` — ship to Grafana Loki
    * ``CloudLoggingHandler`` — GCP / AWS / Azure cloud logging
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from infrastructure.logging.interfaces import ILogFormatter, ILogHandler

if TYPE_CHECKING:
    pass


class ConsoleLogHandler(ILogHandler):
    """Log handler that writes to ``stdout``.

    Args:
        formatter: The :class:`~infrastructure.logging.interfaces.ILogFormatter`
            that controls the output format.
        level: Minimum log level for this handler (defaults to ``DEBUG``).
    """

    def __init__(
        self,
        formatter: ILogFormatter,
        *,
        level: int = logging.DEBUG,
    ) -> None:
        super().__init__(handler_id="console")
        self._formatter = formatter
        self._level = level

    def build(self) -> logging.Handler:
        """Build and return a configured ``StreamHandler`` targeting stdout.

        Returns:
            :class:`logging.StreamHandler` with structlog formatter attached.
        """
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(self._level)
        processor_formatter = self._formatter.build_stdlib_formatter()  # type: ignore[attr-defined]
        handler.setFormatter(processor_formatter)
        return handler


class FileLogHandler(ILogHandler):
    """Log handler that writes plain-text entries to a file.

    Args:
        path: Path to the log file.  Parent directories are created if absent.
        formatter: Output formatter.
        level: Minimum log level.
        encoding: File encoding (default ``"utf-8"``).
    """

    def __init__(
        self,
        path: Path,
        formatter: ILogFormatter,
        *,
        level: int = logging.DEBUG,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__(handler_id="file")
        self._path = path
        self._formatter = formatter
        self._level = level
        self._encoding = encoding

    def build(self) -> logging.Handler:
        """Build and return a ``FileHandler``.

        Creates parent directories if they do not exist.

        Returns:
            :class:`logging.FileHandler` with structlog formatter attached.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(
            filename=self._path,
            encoding=self._encoding,
        )
        handler.setLevel(self._level)
        processor_formatter = self._formatter.build_stdlib_formatter()  # type: ignore[attr-defined]
        handler.setFormatter(processor_formatter)
        return handler

    def is_available(self) -> bool:
        """Return ``True`` if the log directory is writable.

        Returns:
            ``bool``.
        """
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False


class JSONFileLogHandler(ILogHandler):
    """Log handler that writes JSON-formatted entries to a file.

    Identical to :class:`FileLogHandler` except it forces the
    :class:`~infrastructure.logging.formatter.JSONFormatter`.

    Args:
        path: Path to the JSON log file.
        level: Minimum log level.
        encoding: File encoding.
    """

    def __init__(
        self,
        path: Path,
        *,
        level: int = logging.DEBUG,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__(handler_id="json_file")
        self._path = path
        self._level = level
        self._encoding = encoding

    def build(self) -> logging.Handler:
        """Build and return a ``FileHandler`` with JSON output.

        Returns:
            :class:`logging.FileHandler` with JSON structlog formatter attached.
        """
        from infrastructure.logging.formatter import JSONFormatter

        self._path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(
            filename=self._path,
            encoding=self._encoding,
        )
        handler.setLevel(self._level)
        formatter = JSONFormatter(include_timestamp=True, include_caller=False)
        handler.setFormatter(formatter.build_stdlib_formatter())
        return handler

    def is_available(self) -> bool:
        """Return ``True`` if the log directory is writable.

        Returns:
            ``bool``.
        """
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False


class RotatingFileLogHandler(ILogHandler):
    """Log handler that writes to a rotating file (size-based).

    Automatically rolls the log file once it exceeds ``max_bytes`` and
    retains up to ``backup_count`` old files.

    Args:
        path: Path to the log file.
        formatter: Output formatter.
        max_bytes: Maximum file size before rotation (default 10 MB).
        backup_count: Number of old files to retain (default 5).
        level: Minimum log level.
        encoding: File encoding.
    """

    def __init__(
        self,
        path: Path,
        formatter: ILogFormatter,
        *,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 5,
        level: int = logging.DEBUG,
        encoding: str = "utf-8",
    ) -> None:
        super().__init__(handler_id="rotating_file")
        self._path = path
        self._formatter = formatter
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._level = level
        self._encoding = encoding

    def build(self) -> logging.Handler:
        """Build and return a ``RotatingFileHandler``.

        Creates parent directories if they do not exist.

        Returns:
            :class:`logging.handlers.RotatingFileHandler` with structlog
            formatter attached.
        """
        self._path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            filename=self._path,
            maxBytes=self._max_bytes,
            backupCount=self._backup_count,
            encoding=self._encoding,
        )
        handler.setLevel(self._level)
        processor_formatter = self._formatter.build_stdlib_formatter()  # type: ignore[attr-defined]
        handler.setFormatter(processor_formatter)
        return handler

    def is_available(self) -> bool:
        """Return ``True`` if the log directory is writable.

        Returns:
            ``bool``.
        """
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            return True
        except OSError:
            return False
