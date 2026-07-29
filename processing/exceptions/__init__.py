"""Pipeline engine exception hierarchy."""

from __future__ import annotations

from shared.exceptions import RKGBError


class PipelineError(RKGBError):
    """Root exception for all pipeline engine errors."""


class StageNotFoundError(PipelineError):
    """Raised when a requested stage cannot be found in the registry."""


class StageExecutionError(PipelineError):
    """Raised when a pipeline stage raises an unhandled exception."""


class PipelineConfigurationError(PipelineError):
    """Raised when a pipeline is misconfigured."""


class PluginLoadError(PipelineError):
    """Raised when a pipeline plugin cannot be loaded."""
