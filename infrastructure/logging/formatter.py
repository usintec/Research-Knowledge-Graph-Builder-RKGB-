"""Log formatters for the RKGB Logging & Observability Framework.

Two formatters are provided:

* :class:`ConsoleFormatter` — human-readable, colourised output for
  development.  Uses structlog's ``ConsoleRenderer``.
* :class:`JSONFormatter` — machine-parseable JSON for production log
  aggregation (Loki, Datadog, CloudWatch, etc.).  Uses structlog's
  ``JSONRenderer``.

Formatter selection is driven by ``LoggingConfig.format`` so no business
code needs to change when switching between environments.
"""

from __future__ import annotations

from typing import Any

import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import ProcessorFormatter
from structlog.typing import Processor

from infrastructure.logging.interfaces import ILogFormatter


class ConsoleFormatter(ILogFormatter):
    """Human-readable, colourised console formatter for development.

    Uses structlog's ``ConsoleRenderer`` which aligns key-value pairs and
    applies ANSI colour codes when the terminal supports them.

    Args:
        include_timestamp: Whether to prepend a timestamp to each line.
        include_caller: Whether to append ``filename:lineno`` to each entry.
    """

    def __init__(
        self,
        *,
        include_timestamp: bool = True,
        include_caller: bool = False,
    ) -> None:
        self._include_timestamp = include_timestamp
        self._include_caller = include_caller

    @property
    def format_id(self) -> str:
        """Return the formatter identifier.

        Returns:
            ``"console"``
        """
        return "console"

    def build_processors(self) -> list[Any]:  # noqa: ANN401
        """Return the structlog processor chain for console output.

        Returns:
            Ordered list of structlog processors ending with
            :class:`structlog.dev.ConsoleRenderer`.
        """
        processors: list[Processor] = []

        if self._include_timestamp:
            processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))

        processors.extend([
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
        ])

        if self._include_caller:
            processors.append(structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ))

        processors.extend([
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True),
        ])

        return processors  # type: ignore[return-value]

    def build_stdlib_formatter(
        self,
        *,
        include_timestamp: bool | None = None,
        include_caller: bool | None = None,
    ) -> ProcessorFormatter:
        """Build a ``ProcessorFormatter`` for use with stdlib logging handlers.

        Args:
            include_timestamp: Override the constructor setting.
            include_caller: Override the constructor setting.

        Returns:
            Configured :class:`structlog.stdlib.ProcessorFormatter`.
        """
        ts = include_timestamp if include_timestamp is not None else self._include_timestamp
        caller = include_caller if include_caller is not None else self._include_caller

        tmp = ConsoleFormatter(include_timestamp=ts, include_caller=caller)
        return ProcessorFormatter(processors=tmp.build_processors())  # type: ignore[arg-type]


class JSONFormatter(ILogFormatter):
    """Machine-parseable JSON log formatter for production.

    Emits a single-line JSON object per log entry.  Suitable for log
    aggregation stacks (Loki, Elastic, Datadog, CloudWatch).

    Args:
        include_timestamp: Whether to include ``timestamp`` field.
        include_caller: Whether to include ``filename`` / ``lineno`` fields.
        sort_keys: Whether to sort JSON keys alphabetically.
    """

    def __init__(
        self,
        *,
        include_timestamp: bool = True,
        include_caller: bool = False,
        sort_keys: bool = False,
    ) -> None:
        self._include_timestamp = include_timestamp
        self._include_caller = include_caller
        self._sort_keys = sort_keys

    @property
    def format_id(self) -> str:
        """Return the formatter identifier.

        Returns:
            ``"json"``
        """
        return "json"

    def build_processors(self) -> list[Any]:  # noqa: ANN401
        """Return the structlog processor chain for JSON output.

        Returns:
            Ordered list of structlog processors ending with
            :class:`structlog.processors.JSONRenderer`.
        """
        processors: list[Processor] = []

        if self._include_timestamp:
            processors.append(structlog.processors.TimeStamper(fmt="iso", utc=True))

        processors.extend([
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
        ])

        if self._include_caller:
            processors.append(structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ))

        processors.extend([
            structlog.processors.StackInfoRenderer(),
            structlog.processors.ExceptionRenderer(),
            JSONRenderer(sort_keys=self._sort_keys),
        ])

        return processors  # type: ignore[return-value]

    def build_stdlib_formatter(
        self,
        *,
        include_timestamp: bool | None = None,
        include_caller: bool | None = None,
    ) -> ProcessorFormatter:
        """Build a ``ProcessorFormatter`` for use with stdlib logging handlers.

        Args:
            include_timestamp: Override the constructor setting.
            include_caller: Override the constructor setting.

        Returns:
            Configured :class:`structlog.stdlib.ProcessorFormatter`.
        """
        ts = include_timestamp if include_timestamp is not None else self._include_timestamp
        caller = include_caller if include_caller is not None else self._include_caller

        tmp = JSONFormatter(include_timestamp=ts, include_caller=caller, sort_keys=self._sort_keys)
        return ProcessorFormatter(processors=tmp.build_processors())  # type: ignore[arg-type]


def build_formatter(
    format_id: str,
    *,
    include_timestamp: bool = True,
    include_caller: bool = False,
) -> ILogFormatter:
    """Factory function that returns the correct formatter for a format identifier.

    Args:
        format_id: ``"console"`` or ``"json"``.
        include_timestamp: Whether to include timestamps.
        include_caller: Whether to include caller info.

    Returns:
        :class:`ILogFormatter` instance.

    Raises:
        :class:`~infrastructure.logging.exceptions.FormatterNotFoundError`:
            If the format identifier is unrecognised.
    """
    from infrastructure.logging.exceptions import FormatterNotFoundError

    match format_id:
        case "console":
            return ConsoleFormatter(
                include_timestamp=include_timestamp,
                include_caller=include_caller,
            )
        case "json":
            return JSONFormatter(
                include_timestamp=include_timestamp,
                include_caller=include_caller,
            )
        case _:
            raise FormatterNotFoundError(format_id)
