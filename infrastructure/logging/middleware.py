"""Logging middleware abstractions for the RKGB platform.

Middleware components automatically instrument cross-cutting concerns so
that business code does not contain explicit logging calls for lifecycle
events (start, complete, fail, duration).

These are **abstractions only** — the concrete FastAPI HTTP middleware is
implemented in a later step.  The pipeline, command, query, and event
middleware classes here are ready to be wired into those engines.

Design
------
Each middleware is a context manager (``async with`` or ``with``) that:

1. Logs the *started* event and sets the correlation context.
2. Yields control to the wrapped code.
3. Logs *completed* or *failed* depending on whether an exception occurred.
4. Restores the previous correlation context via the ``contextvars`` token.

Usage — Pipeline Stage (future pipeline engine integration)::

    async with PipelineStageMiddleware(logger, ctx, stage_id="stage-1"):
        await stage.execute(context)

Usage — Command Bus (future command bus integration)::

    async with CommandMiddleware(logger, ctx, command_name="CreateDocumentCommand"):
        result = await handler.handle(command)
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Any, AsyncIterator, Iterator

if TYPE_CHECKING:
    from infrastructure.logging.logger import RKGBLogger
    from infrastructure.logging.models.context import CorrelationContext


# ---------------------------------------------------------------------------
# Pipeline stage middleware
# ---------------------------------------------------------------------------


@contextmanager
def pipeline_stage_logging(
    logger: "RKGBLogger",
    ctx: "CorrelationContext",
    *,
    stage_id: str,
    pipeline_id: str | None = None,
) -> Iterator[None]:
    """Context manager that automatically logs pipeline stage lifecycle events.

    Logs ``pipeline_stage_started``, ``pipeline_stage_completed``, and
    ``pipeline_stage_failed`` without requiring the pipeline engine to call
    the logger directly.

    Args:
        logger: Logger instance (usually bound to ``"rkgb.pipeline"``).
        ctx: Active correlation context for this execution.
        stage_id: Unique identifier of the pipeline stage.
        pipeline_id: Optional pipeline identifier for the log entry.

    Yields:
        Control to the calling code.
    """
    from infrastructure.logging.context import reset_correlation_context, set_correlation_context

    stage_ctx = ctx.with_stage(stage_id=stage_id)
    if pipeline_id:
        stage_ctx = stage_ctx.with_pipeline(pipeline_id=pipeline_id)

    token = set_correlation_context(stage_ctx)
    start = time.monotonic()
    extra: dict[str, Any] = {}
    if pipeline_id:
        extra["pipeline_id"] = pipeline_id

    logger.log_pipeline_stage_started(stage_id, **extra)
    try:
        yield
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_pipeline_stage_failed(stage_id, exc, duration_ms=duration_ms, **extra)
        raise
    else:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_pipeline_stage_completed(stage_id, duration_ms=duration_ms, **extra)
    finally:
        reset_correlation_context(token)


@asynccontextmanager
async def async_pipeline_stage_logging(
    logger: "RKGBLogger",
    ctx: "CorrelationContext",
    *,
    stage_id: str,
    pipeline_id: str | None = None,
) -> AsyncIterator[None]:
    """Async version of :func:`pipeline_stage_logging`.

    Args:
        logger: Logger instance.
        ctx: Active correlation context.
        stage_id: Unique stage identifier.
        pipeline_id: Optional pipeline identifier.

    Yields:
        Control to the calling async code.
    """
    from infrastructure.logging.context import reset_correlation_context, set_correlation_context

    stage_ctx = ctx.with_stage(stage_id=stage_id)
    if pipeline_id:
        stage_ctx = stage_ctx.with_pipeline(pipeline_id=pipeline_id)

    token = set_correlation_context(stage_ctx)
    start = time.monotonic()
    extra: dict[str, Any] = {}
    if pipeline_id:
        extra["pipeline_id"] = pipeline_id

    logger.log_pipeline_stage_started(stage_id, **extra)
    try:
        yield
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_pipeline_stage_failed(stage_id, exc, duration_ms=duration_ms, **extra)
        raise
    else:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_pipeline_stage_completed(stage_id, duration_ms=duration_ms, **extra)
    finally:
        reset_correlation_context(token)


# ---------------------------------------------------------------------------
# Command bus middleware
# ---------------------------------------------------------------------------


@asynccontextmanager
async def command_logging(
    logger: "RKGBLogger",
    ctx: "CorrelationContext",
    *,
    command_name: str,
) -> AsyncIterator[None]:
    """Async context manager for command bus lifecycle logging.

    Logs ``command_dispatched``, ``command_completed``, and
    ``command_failed`` automatically.

    Intended for use inside the Command Bus implementation (future step).
    No Command Bus code is created here — only the logging instrumentation.

    Args:
        logger: Logger bound to the command bus component.
        ctx: Active correlation context.
        command_name: Fully-qualified command class name.

    Yields:
        Control to the command handler.
    """
    from infrastructure.logging.context import reset_correlation_context, set_correlation_context

    cmd_ctx = ctx.with_command(command_name=command_name)
    token = set_correlation_context(cmd_ctx)
    start = time.monotonic()

    logger.log_command_dispatched(command_name)
    try:
        yield
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_command_failed(command_name, exc, duration_ms=duration_ms)
        raise
    else:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_command_completed(command_name, duration_ms=duration_ms)
    finally:
        reset_correlation_context(token)


# ---------------------------------------------------------------------------
# Query bus middleware
# ---------------------------------------------------------------------------


@asynccontextmanager
async def query_logging(
    logger: "RKGBLogger",
    ctx: "CorrelationContext",
    *,
    query_name: str,
) -> AsyncIterator[None]:
    """Async context manager for query bus lifecycle logging.

    Logs ``query_dispatched``, ``query_completed``, and handles failures.

    Args:
        logger: Logger bound to the query bus component.
        ctx: Active correlation context.
        query_name: Fully-qualified query class name.

    Yields:
        Control to the query handler.
    """
    from infrastructure.logging.context import reset_correlation_context, set_correlation_context

    query_ctx = ctx.with_query(query_name=query_name)
    token = set_correlation_context(query_ctx)
    start = time.monotonic()

    logger.log_query_dispatched(query_name)
    try:
        yield
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000
        from infrastructure.logging.models.log_entry import ExceptionInfo

        logger.error(
            "query_failed",
            query_name=query_name,
            duration_ms=duration_ms,
            exception=ExceptionInfo.from_exception(exc).to_dict(),
        )
        raise
    else:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_query_completed(query_name, duration_ms=duration_ms)
    finally:
        reset_correlation_context(token)


# ---------------------------------------------------------------------------
# Event bus middleware
# ---------------------------------------------------------------------------


@asynccontextmanager
async def event_logging(
    logger: "RKGBLogger",
    ctx: "CorrelationContext",
    *,
    event_name: str,
    subscriber: str,
) -> AsyncIterator[None]:
    """Async context manager for event bus subscriber lifecycle logging.

    Logs ``event_subscriber_invoked``, ``event_subscriber_completed``, and
    handles subscriber failures including future retry logic.

    Args:
        logger: Logger bound to the event bus component.
        ctx: Active correlation context.
        event_name: Fully-qualified event class name.
        subscriber: Name of the event subscriber handler.

    Yields:
        Control to the subscriber handler.
    """
    from infrastructure.logging.context import reset_correlation_context, set_correlation_context

    event_ctx = ctx.with_event(event_name=event_name)
    token = set_correlation_context(event_ctx)
    start = time.monotonic()

    logger.log_event_subscriber_invoked(event_name, subscriber)
    try:
        yield
    except Exception as exc:
        duration_ms = (time.monotonic() - start) * 1000
        from infrastructure.logging.models.log_entry import ExceptionInfo

        logger.error(
            "event_subscriber_failed",
            event_name=event_name,
            subscriber=subscriber,
            duration_ms=duration_ms,
            exception=ExceptionInfo.from_exception(exc).to_dict(),
        )
        raise
    else:
        duration_ms = (time.monotonic() - start) * 1000
        logger.log_event_subscriber_completed(
            event_name, subscriber, duration_ms=duration_ms
        )
    finally:
        reset_correlation_context(token)
