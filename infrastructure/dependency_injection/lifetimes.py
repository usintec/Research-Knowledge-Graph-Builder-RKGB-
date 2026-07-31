"""Service lifetime definitions for the RKGB Dependency Injection Framework.

Three lifetimes are supported — matching the standard DI lifetime model used
by frameworks such as Microsoft.Extensions.DependencyInjection and Spring:

* **Singleton** — one instance per application process.
* **Scoped** — one instance per execution scope (HTTP request, pipeline run…).
* **Transient** — a fresh instance on every resolution.
"""

from __future__ import annotations

from enum import Enum, auto


class ServiceLifetime(Enum):
    """Controls how long a resolved service instance is retained.

    Attributes:
        SINGLETON: One instance for the entire application lifetime.
            The instance is created on the first resolution and reused
            for every subsequent resolution. Examples: ConfigManager,
            LoggingManager, CommandBus, QueryBus, EventBus, PluginRegistry.
        SCOPED: One instance per execution scope.
            A scope is an isolated context — an HTTP request, a pipeline
            execution, a CLI command, or a Kafka message. Scoped instances
            are discarded when the scope exits. Examples: PipelineContext,
            RequestContext, CorrelationContext.
        TRANSIENT: A new instance is created on every resolution.
            No caching is performed; callers always receive a fresh object.
            Examples: CommandHandlers, QueryHandlers, Validators, Policies.
    """

    SINGLETON = auto()
    SCOPED = auto()
    TRANSIENT = auto()
