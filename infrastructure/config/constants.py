"""Constants used throughout the RKGB Configuration Framework.

Centralising magic values here prevents string literals from scattering
across the codebase and makes future refactoring safe.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Provider priorities
# ---------------------------------------------------------------------------

#: Priority for hard-coded default values embedded in Pydantic models.
PRIORITY_DEFAULTS: int = 10

#: Priority for the base ``configs/base.yaml`` file (not environment-specific).
PRIORITY_BASE_YAML: int = 20

#: Priority for the environment-specific YAML (e.g. ``configs/production.yaml``).
PRIORITY_ENV_YAML: int = 30

#: Priority for OS environment variables.
PRIORITY_ENV_VARS: int = 40

#: Priority for runtime overrides injected programmatically (e.g. in tests).
PRIORITY_RUNTIME: int = 50

# ---------------------------------------------------------------------------
# Environment variable names
# ---------------------------------------------------------------------------

#: Name of the env var that selects the current deployment environment.
ENV_VAR_APP_ENV: str = "APP_ENV"

#: Prefix applied to all RKGB-specific environment variables.
ENV_VAR_PREFIX: str = "RKGB_"

# ---------------------------------------------------------------------------
# File system
# ---------------------------------------------------------------------------

#: Default directory (relative to project root) for YAML config files.
DEFAULT_CONFIG_DIR: str = "configs"

#: Base YAML filename loaded before the environment-specific one.
BASE_CONFIG_FILENAME: str = "base.yaml"

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

#: Cache key used to store the fully resolved RootConfig.
CACHE_KEY_ROOT: str = "root"

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

#: Key under which the feature-flags section is registered.
REGISTRY_KEY_FEATURE_FLAGS: str = "feature_flags"

#: Key under which the application section is registered.
REGISTRY_KEY_APPLICATION: str = "application"

# ---------------------------------------------------------------------------
# Sentinel
# ---------------------------------------------------------------------------

#: Sentinel object used to distinguish "not set" from ``None``.
UNSET: object = object()
