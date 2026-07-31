"""Unit tests for CompositionRoot and bootstrap helpers.

Covers:
    * CompositionRoot.build() returns a ServiceProvider.
    * ConfigManager resolved from the built provider.
    * LoggingManager resolved from the built provider.
    * LoggerFactory resolved from the built provider.
    * All typed config sections are resolvable.
    * extra_modules are applied after standard modules.
    * skip_validation=True bypasses startup validation.
    * build_test_container() works without explicit args.
    * build_test_container() accepts pre-built config and logging.
"""

from __future__ import annotations

import pytest

from infrastructure.config.bootstrap import bootstrap_config
from infrastructure.config.manager import ConfigManager
from infrastructure.config.models import ApplicationConfig, LoggingConfig, Neo4jConfig
from infrastructure.dependency_injection.bootstrap import bootstrap_container, build_test_container
from infrastructure.dependency_injection.composition_root import CompositionRoot
from infrastructure.dependency_injection.service_collection import ServiceCollection
from infrastructure.dependency_injection.service_provider import ServiceProvider
from infrastructure.logging.bootstrap import bootstrap_logging
from infrastructure.logging.factory import LoggerFactory
from infrastructure.logging.manager import LoggingManager


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def config_manager() -> ConfigManager:
    return bootstrap_config()


@pytest.fixture(scope="module")
def logging_manager(config_manager: ConfigManager) -> LoggingManager:
    return bootstrap_logging(config_manager)


# ---------------------------------------------------------------------------
# CompositionRoot
# ---------------------------------------------------------------------------


class TestCompositionRoot:
    def test_build_returns_service_provider(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        assert isinstance(provider, ServiceProvider)

    def test_resolves_config_manager(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        resolved = provider.resolve(ConfigManager)
        assert resolved is config_manager

    def test_resolves_logging_manager(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        resolved = provider.resolve(LoggingManager)
        assert resolved is logging_manager

    def test_resolves_logger_factory(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        factory = provider.resolve(LoggerFactory)
        assert isinstance(factory, LoggerFactory)

    def test_resolves_config_sections(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        app_cfg = provider.resolve(ApplicationConfig)
        log_cfg = provider.resolve(LoggingConfig)
        neo4j_cfg = provider.resolve(Neo4jConfig)
        assert isinstance(app_cfg, ApplicationConfig)
        assert isinstance(log_cfg, LoggingConfig)
        assert isinstance(neo4j_cfg, Neo4jConfig)

    def test_extra_modules_are_applied(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        class ExtraService:
            pass

        class ExtraModule:
            def register(self, services: ServiceCollection) -> None:
                services.add_singleton(ExtraService)

        root = CompositionRoot(
            config_manager,
            logging_manager,
            extra_modules=[ExtraModule()],
            skip_validation=True,
        )
        provider = root.build()
        instance = provider.resolve(ExtraService)
        assert isinstance(instance, ExtraService)

    def test_config_manager_singleton_is_same_instance(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        root = CompositionRoot(config_manager, logging_manager, skip_validation=True)
        provider = root.build()
        a = provider.resolve(ConfigManager)
        b = provider.resolve(ConfigManager)
        assert a is b


# ---------------------------------------------------------------------------
# bootstrap_container helper
# ---------------------------------------------------------------------------


class TestBootstrapContainer:
    def test_returns_service_provider(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        provider = bootstrap_container(
            config_manager, logging_manager, skip_validation=True
        )
        assert isinstance(provider, ServiceProvider)

    def test_resolves_core_services(
        self, config_manager: ConfigManager, logging_manager: LoggingManager
    ) -> None:
        provider = bootstrap_container(
            config_manager, logging_manager, skip_validation=True
        )
        assert provider.resolve(ConfigManager) is config_manager
        assert provider.resolve(LoggingManager) is logging_manager
        assert isinstance(provider.resolve(LoggerFactory), LoggerFactory)


# ---------------------------------------------------------------------------
# build_test_container helper
# ---------------------------------------------------------------------------


class TestBuildTestContainer:
    def test_no_args_builds_successfully(self) -> None:
        provider = build_test_container()
        assert isinstance(provider, ServiceProvider)

    def test_resolves_config_manager_without_args(self) -> None:
        provider = build_test_container()
        assert isinstance(provider.resolve(ConfigManager), ConfigManager)

    def test_resolves_logging_manager_without_args(self) -> None:
        provider = build_test_container()
        assert isinstance(provider.resolve(LoggingManager), LoggingManager)

    def test_resolves_logger_factory_without_args(self) -> None:
        provider = build_test_container()
        assert isinstance(provider.resolve(LoggerFactory), LoggerFactory)

    def test_accepts_pre_built_config_manager(
        self, config_manager: ConfigManager
    ) -> None:
        provider = build_test_container(config_manager=config_manager)
        resolved = provider.resolve(ConfigManager)
        assert resolved is config_manager

    def test_accepts_pre_built_logging_manager(
        self, logging_manager: LoggingManager
    ) -> None:
        provider = build_test_container(logging_manager=logging_manager)
        resolved = provider.resolve(LoggingManager)
        assert resolved is logging_manager

    def test_extra_modules_work_in_test_container(self) -> None:
        class TestService:
            pass

        class TestModule:
            def register(self, services: ServiceCollection) -> None:
                services.add_singleton(TestService)

        provider = build_test_container(extra_modules=[TestModule()])
        instance = provider.resolve(TestService)
        assert isinstance(instance, TestService)
