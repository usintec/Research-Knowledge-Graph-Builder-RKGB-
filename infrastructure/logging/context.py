"""Correlation context management via Python ``contextvars``.

``contextvars.ContextVar`` ensures the correlation context flows correctly
through async tasks, thread pools, and pipeline stages without requiring
explicit parameter passing throughout the call stack.

Every entry point (HTTP handler, CLI command, pipeline run, event subscriber)
should call :func:`set_correlation_context` at the top level.  Downstream
code reads it via :func:`get_correlation_context`.

Usage::

    from infrastructure.logging.context import (
        set_correlation_context,
        get_correlation_context,
        clear_correlation_context,
        bind_context_to_structlog,
    )
    from infrastructure.logging.models.context import CorrelationContext
    from infrastructure.logging.correlation import generate_correlation_id

    # At the entry point:
    ctx = CorrelationContext(correlation_id=generate_correlation_id())
    token = set_correlation_context(ctx)

    # ... application code runs ...

    # To restore previous context (e.g. in middleware):
    reset_correlation_context(token)
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from infrastructure.logging.models.context import CorrelationContext


# ---------------------------------------------------------------------------
# Module-level ContextVar — one per process, shared across all async tasks.
# ---------------------------------------------------------------------------

_CORRELATION_CONTEXT_VAR: ContextVar["CorrelationContext | None"] = ContextVar(
    "rkgb_correlation_context",
    default=None,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def set_correlation_context(ctx: "CorrelationContext") -> "Token[CorrelationContext | None]":
    """Set the active correlation context for the current task/thread.

    Calling this automatically binds all context fields to structlog's
    context-vars storage so every subsequent log call carries them without
    explicit ``bind()`` calls.

    Args:
        ctx: The :class:`~infrastructure.logging.models.context.CorrelationContext`
            to activate.

    Returns:
        A ``Token`` that can be passed to :func:`reset_correlation_context`
        to restore the previous context (useful in middleware).
    """
    token = _CORRELATION_CONTEXT_VAR.set(ctx)
    bind_context_to_structlog(ctx)
    return token


def get_correlation_context() -> "CorrelationContext | None":
    """Return the active correlation context, or ``None`` if unset.

    Returns:
        :class:`~infrastructure.logging.models.context.CorrelationContext`
        or ``None``.
    """
    return _CORRELATION_CONTEXT_VAR.get()


def reset_correlation_context(token: "Token[CorrelationContext | None]") -> None:
    """Restore the previous correlation context using a token.

    This is the counterpart to :func:`set_correlation_context`.  Call it in a
    ``finally`` block or middleware teardown to avoid context leaks.

    Args:
        token: The token returned by :func:`set_correlation_context`.
    """
    _CORRELATION_CONTEXT_VAR.reset(token)
    previous = _CORRELATION_CONTEXT_VAR.get()
    if previous is not None:
        bind_context_to_structlog(previous)
    else:
        structlog.contextvars.clear_contextvars()


def clear_correlation_context() -> None:
    """Clear the correlation context entirely for the current task/thread.

    Also clears structlog's context-var bindings.  Use when you need a
    completely fresh context (e.g. in test teardown).
    """
    _CORRELATION_CONTEXT_VAR.set(None)
    structlog.contextvars.clear_contextvars()


def bind_context_to_structlog(ctx: "CorrelationContext") -> None:
    """Push all context fields into structlog's context-var storage.

    This makes every log call in the current async task automatically include
    the full correlation context without any explicit ``bind()`` calls.

    Args:
        ctx: The context whose fields should be bound.
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(**ctx.to_log_dict())
