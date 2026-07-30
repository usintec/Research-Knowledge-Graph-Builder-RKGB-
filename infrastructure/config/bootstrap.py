"""Configuration bootstrap module.

This module is the single call site for assembling the ``ConfigManager``
from all available providers and handing it to the application.

**Call ``bootstrap_config()`` once at startup** — typically inside the
FastAPI lifespan handler or the CLI entrypoint.  All components should
receive their configuration via the DI container (next step), not by
calling this function directly.

Bootstrap sequence:
    1. Detect the active :class:`~infrastructure.config.environment.Environment`.
    2. Construct providers (YAML base, YAML env-specific, OS env vars).
    3. Build the :class:`~infrastructure.config.manager.ConfigManager`.
    4. Call ``manager.load()`` — merge, validate, cache.
    5. Return the manager for registration with the DI container.

DI container integration (preview — implemented in Step A3)::

    manager = bootstrap_config()
    container.define(ConfigManager, lambda: manager)
    container.define(Neo4jConfig, lambda: manager.get(Neo4jConfig))
    # ... register other sections ...
"""

from __future__ import annotations

from pathlib import Path

from infrastructure.config.constants import PRIORITY_BASE_YAML, PRIORITY_ENV_YAML
from infrastructure.config.environment import Environment
from infrastructure.config.manager import ConfigManager
from infrastructure.config.models.root import RootConfig
from infrastructure.config.providers.env_provider import EnvProvider
from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider, YAMLProvider


def bootstrap_config(
    config_dir: Path | str | None = None,
    env: Environment | None = None,
    overrides: dict[str, object] | None = None,
) -> ConfigManager:
    """Assemble and initialise the ``ConfigManager``.

    Args:
        config_dir: Path to the directory containing YAML config files.
            Defaults to ``./configs/`` relative to the current working dir.
        env: Override the auto-detected environment.  Pass ``None`` to let
            the manager read ``APP_ENV`` from the environment.
        overrides: Optional dict of runtime overrides applied at highest
            priority.  Useful for programmatic configuration in tests.

    Returns:
        Initialised :class:`~infrastructure.config.manager.ConfigManager`
        with configuration loaded and cached.

    Example::

        from infrastructure.config.bootstrap import bootstrap_config
        from infrastructure.config.models import Neo4jConfig

        manager = bootstrap_config()
        neo4j: Neo4jConfig = manager.get(Neo4jConfig)
    """
    resolved_env = env or Environment.current()
    resolved_dir = Path(config_dir) if config_dir else Path.cwd() / "configs"

    providers = _build_providers(resolved_dir, resolved_env, overrides or {})
    manager = ConfigManager(providers=providers, env=resolved_env)
    manager.load()
    return manager


def _build_providers(
    config_dir: Path,
    env: Environment,
    overrides: dict[str, object],
) -> list[object]:
    """Build the ordered provider list for the given environment.

    Args:
        config_dir: Config file directory.
        env: Active environment.
        overrides: Runtime override dict.

    Returns:
        List of :class:`~infrastructure.config.interfaces.ConfigProvider` instances.
    """
    providers: list[object] = []

    # 1. Base YAML (optional — missing is not an error)
    base_yaml = config_dir / "base.yaml"
    providers.append(
        YAMLProvider(path=base_yaml, priority=PRIORITY_BASE_YAML, optional=True)
    )

    # 2. Environment-specific YAML (optional)
    env_yaml = config_dir / env.config_file_name
    providers.append(
        YAMLProvider(path=env_yaml, priority=PRIORITY_ENV_YAML, optional=True)
    )

    # 3. OS environment variables (always active)
    providers.append(EnvProvider())

    # 4. Runtime overrides (only added when non-empty)
    if overrides:
        providers.append(RuntimeOverrideProvider(overrides=overrides))  # type: ignore[arg-type]

    return providers  # type: ignore[return-value]


def build_test_config(overrides: dict[str, object] | None = None) -> RootConfig:
    """Build a minimal configuration suitable for unit tests.

    No files are read; all values come from Pydantic defaults and the
    optional *overrides* dict.  This guarantees tests are hermetic and
    fast.

    Args:
        overrides: Optional nested dict of configuration overrides.

    Returns:
        Fully validated :class:`~infrastructure.config.models.root.RootConfig`.

    Example::

        root = build_test_config({"neo4j": {"database": "test"}})
        assert root.neo4j.database == "test"
    """
    from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider

    base_override = {"application": {"env": "testing"}}
    if overrides:
        from infrastructure.config.resolver import _deep_merge

        base_override = _deep_merge(base_override, overrides)  # type: ignore[arg-type]

    manager = ConfigManager(
        providers=[RuntimeOverrideProvider(overrides=base_override)],
        env=Environment.TESTING,
    )
    return manager.load()
