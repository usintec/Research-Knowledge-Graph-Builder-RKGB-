"""Tests for the Environment abstraction."""

from __future__ import annotations

import pytest

from infrastructure.config.environment import Environment


@pytest.mark.unit()
class TestEnvironmentEnum:
    """Tests for Environment value resolution."""

    def test_all_values_are_valid_strings(self) -> None:
        expected = {"local", "development", "testing", "staging", "production", "docker", "ci"}
        actual = {e.value for e in Environment}
        assert actual == expected

    def test_current_defaults_to_development(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("APP_ENV", raising=False)
        assert Environment.current() == Environment.DEVELOPMENT

    def test_current_reads_app_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_ENV", "production")
        assert Environment.current() == Environment.PRODUCTION

    def test_current_falls_back_on_unknown_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("APP_ENV", "garbage")
        assert Environment.current() == Environment.DEVELOPMENT

    def test_is_production_true_for_production(self) -> None:
        assert Environment.PRODUCTION.is_production is True

    def test_is_production_true_for_staging(self) -> None:
        assert Environment.STAGING.is_production is True

    def test_is_production_false_for_development(self) -> None:
        assert Environment.DEVELOPMENT.is_production is False

    def test_is_development_true_for_local(self) -> None:
        assert Environment.LOCAL.is_development is True

    def test_is_development_true_for_docker(self) -> None:
        assert Environment.DOCKER.is_development is True

    def test_is_testing_true_for_ci(self) -> None:
        assert Environment.CI.is_testing is True

    def test_config_file_name_matches_value(self) -> None:
        assert Environment.PRODUCTION.config_file_name == "production.yaml"
        assert Environment.DEVELOPMENT.config_file_name == "development.yaml"
