"""Configuration file loader utilities.

Provides helper functions and a ``ConfigFileLoader`` class for
discovering and reading configuration files from the filesystem.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from infrastructure.config.constants import BASE_CONFIG_FILENAME, DEFAULT_CONFIG_DIR
from infrastructure.config.environment import Environment
from infrastructure.config.exceptions import ConfigLoadError


class ConfigFileLoader:
    """Discovers and reads configuration YAML files.

    Handles the convention:
        ``<config_dir>/base.yaml``        — always loaded (optional)
        ``<config_dir>/<env>.yaml``       — environment-specific (optional)

    Args:
        config_dir: Directory containing YAML config files.
            Defaults to ``configs/`` relative to the current working dir.
    """

    def __init__(self, config_dir: Path | str | None = None) -> None:
        self._config_dir = (
            Path(config_dir) if config_dir else Path.cwd() / DEFAULT_CONFIG_DIR
        )

    @property
    def config_dir(self) -> Path:
        """Configuration directory path.

        Returns:
            Resolved ``Path`` to the config directory.
        """
        return self._config_dir

    def base_config_path(self) -> Path:
        """Return the path for ``base.yaml``.

        Returns:
            ``Path`` to base config file (may not exist).
        """
        return self._config_dir / BASE_CONFIG_FILENAME

    def env_config_path(self, env: Environment) -> Path:
        """Return the path for the environment-specific YAML file.

        Args:
            env: The active deployment environment.

        Returns:
            ``Path`` to the environment config file (may not exist).
        """
        return self._config_dir / env.config_file_name

    def load_yaml(self, path: Path) -> dict[str, Any]:
        """Read and parse a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            Parsed dictionary, or ``{}`` if the file does not exist.

        Raises:
            ConfigLoadError: If the file exists but cannot be parsed.
        """
        if not path.is_file():
            return {}

        try:
            raw = path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            return data if isinstance(data, dict) else {}
        except yaml.YAMLError as exc:
            raise ConfigLoadError(source=str(path), reason=f"YAML parse error: {exc}") from exc
        except OSError as exc:
            raise ConfigLoadError(source=str(path), reason=f"I/O error: {exc}") from exc

    def load_for_environment(self, env: Environment) -> tuple[dict[str, Any], dict[str, Any]]:
        """Load both base and env-specific YAML for the given environment.

        Args:
            env: The active environment.

        Returns:
            Tuple of ``(base_data, env_data)`` dictionaries.
        """
        base_data = self.load_yaml(self.base_config_path())
        env_data = self.load_yaml(self.env_config_path(env))
        return base_data, env_data
