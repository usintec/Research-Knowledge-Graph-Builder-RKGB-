"""Environment abstraction for RKGB.

Provides a strongly typed ``Environment`` enum and helper utilities so
that no component ever compares raw strings like ``"production"`` or
reads ``APP_ENV`` directly.

Usage::

    from infrastructure.config.environment import Environment

    env = Environment.current()

    if env.is_production:
        ...
"""

from __future__ import annotations

import os
from enum import StrEnum


class Environment(StrEnum):
    """Supported deployment environments.

    Inherits ``StrEnum`` so instances can be used wherever a plain string is
    expected (e.g. as YAML keys, log fields) without an explicit cast.
    """

    LOCAL = "local"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DOCKER = "docker"
    CI = "ci"

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def current(cls) -> Environment:
        """Resolve the active environment from the ``APP_ENV`` env var.

        Falls back to :attr:`DEVELOPMENT` when the variable is absent or
        contains an unrecognised value.

        Returns:
            The resolved :class:`Environment`.
        """
        raw = os.environ.get("APP_ENV", "development").strip().lower()
        try:
            return cls(raw)
        except ValueError:
            return cls.DEVELOPMENT

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    @property
    def is_production(self) -> bool:
        """Return ``True`` for production-like environments.

        Returns:
            ``True`` for :attr:`PRODUCTION` and :attr:`STAGING`.
        """
        return self in (Environment.PRODUCTION, Environment.STAGING)

    @property
    def is_development(self) -> bool:
        """Return ``True`` for developer-facing environments.

        Returns:
            ``True`` for :attr:`LOCAL`, :attr:`DEVELOPMENT`, and :attr:`DOCKER`.
        """
        return self in (Environment.LOCAL, Environment.DEVELOPMENT, Environment.DOCKER)

    @property
    def is_testing(self) -> bool:
        """Return ``True`` for test / CI environments.

        Returns:
            ``True`` for :attr:`TESTING` and :attr:`CI`.
        """
        return self in (Environment.TESTING, Environment.CI)

    @property
    def config_file_name(self) -> str:
        """Return the conventional YAML config filename for this environment.

        Returns:
            Filename string, e.g. ``"development.yaml"``.
        """
        return f"{self.value}.yaml"
