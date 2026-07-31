"""Logging registration module.

Registers :class:`~infrastructure.logging.manager.LoggingManager` and
:class:`~infrastructure.logging.factory.LoggerFactory` as application-lifetime
singletons so that every component receives the same configured logging
infrastructure through constructor injection.

This module is always applied immediately after
:class:`~.configuration_module.ConfigurationModule`.
"""

from __future__ import annotations

from infrastructure.dependency_injection.interfaces import IServiceCollection
from infrastructure.logging.factory import LoggerFactory
from infrastructure.logging.manager import LoggingManager


class LoggingModule:
    """Registers the logging infrastructure as singletons.

    Args:
        logging_manager: The initialised
            :class:`~infrastructure.logging.manager.LoggingManager` produced
            during startup by
            :func:`~infrastructure.logging.bootstrap.bootstrap_logging`.
    """

    def __init__(self, logging_manager: LoggingManager) -> None:
        self._logging_manager = logging_manager

    def register(self, services: IServiceCollection) -> None:
        """Register logging services.

        Registered services:
            - :class:`~infrastructure.logging.manager.LoggingManager`
              (singleton, pre-built instance).
            - :class:`~infrastructure.logging.factory.LoggerFactory`
              (singleton, resolved via the manager's ``factory`` property).

        Args:
            services: The service collection to register into.
        """
        manager = self._logging_manager

        services.add_singleton(LoggingManager, instance=manager)
        services.add_singleton(
            LoggerFactory,
            factory=lambda p: p.resolve(LoggingManager).factory,
        )
