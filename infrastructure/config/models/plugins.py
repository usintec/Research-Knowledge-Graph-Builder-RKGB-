"""Plugin system configuration model.

Plugins can contribute their own configuration sections which are
registered with the ConfigRegistry during bootstrap.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PluginConfig(BaseModel):
    """Configuration for the plugin discovery and loading system."""

    model_config = ConfigDict(frozen=True)

    enabled: bool = False
    scan_paths: list[str] = Field(default_factory=list)
    plugin_config_dir: str = "./plugins/config"
    allow_external_plugins: bool = False
    strict_validation: bool = True  # Reject plugins with invalid config
    auto_discover: bool = True


class PluginManifestConfig(BaseModel):
    """Per-plugin manifest configuration contributed via the registry.

    Third-party plugins subclass or instantiate this to declare their
    own configuration schema.
    """

    model_config = ConfigDict(frozen=True)

    name: str
    version: str = "0.1.0"
    enabled: bool = True
    settings: dict[str, object] = Field(default_factory=dict)
