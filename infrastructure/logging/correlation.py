"""Correlation and trace ID generation for the RKGB Logging Framework.

Provides a default :class:`UUIDCorrelationProvider` that generates RFC 4122
UUIDs.  The interface is designed so that future implementations can produce
OTEL-compatible 128-bit trace IDs or shortened identifiers for log readability
without touching any call sites.

Usage::

    from infrastructure.logging.correlation import UUIDCorrelationProvider

    provider = UUIDCorrelationProvider()
    correlation_id = provider.generate_correlation_id()
    trace_id = provider.generate_trace_id()
"""

from __future__ import annotations

import uuid

from infrastructure.logging.interfaces import ICorrelationProvider


class UUIDCorrelationProvider:
    """Default correlation provider using UUID4.

    Produces RFC 4122 v4 UUIDs as correlation and trace identifiers.
    These are universally unique, require no central coordination, and are
    human-readable in log output.

    When OpenTelemetry integration is added, this class can be replaced with
    an OTEL-aware provider that reads the active span's trace/span IDs.
    """

    def generate_correlation_id(self) -> str:
        """Generate a new correlation ID as a UUID4 string.

        Returns:
            Hyphenated UUID4 string, e.g. ``"3a8f1b2c-4d5e-..."``.
        """
        return str(uuid.uuid4())

    def generate_trace_id(self) -> str:
        """Generate a new OTEL-compatible trace ID.

        Returns a 32-character lowercase hex string (128 bits) — the same
        format used by OpenTelemetry trace IDs, so the value can be used
        directly once OTEL is integrated.

        Returns:
            32-character hex string.
        """
        return uuid.uuid4().hex


# Verify the provider satisfies the protocol at import time.
assert isinstance(UUIDCorrelationProvider(), ICorrelationProvider)


def generate_correlation_id() -> str:
    """Module-level convenience function for generating a correlation ID.

    Uses the default :class:`UUIDCorrelationProvider`.

    Returns:
        Hyphenated UUID4 string.
    """
    return UUIDCorrelationProvider().generate_correlation_id()


def generate_trace_id() -> str:
    """Module-level convenience function for generating a trace ID.

    Uses the default :class:`UUIDCorrelationProvider`.

    Returns:
        32-character hex string.
    """
    return UUIDCorrelationProvider().generate_trace_id()
