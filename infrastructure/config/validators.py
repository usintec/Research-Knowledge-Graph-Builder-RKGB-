"""Configuration validation helpers.

Provides a composable validation framework on top of Pydantic's built-in
field validation.  Post-model-construction validators can be registered
per configuration section to enforce cross-field rules that cannot be
expressed as single-field ``field_validator`` constraints.

Usage::

    registry = ValidationRegistry()

    @registry.register(Neo4jConfig)
    def require_password_in_prod(config: Neo4jConfig, env: Environment) -> None:
        if env.is_production and not config.auth.password:
            raise ConfigValidationError("neo4j", "Password is required in production.")

    registry.validate_all(root_config, env)
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from infrastructure.config.environment import Environment
from infrastructure.config.exceptions import ConfigValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)

# Type alias for a cross-field validator function.
ValidatorFn = Callable[[Any, Environment], None]


class ValidationRegistry:
    """Registry of cross-field validators for configuration models.

    Validators are keyed by model *type* and called after Pydantic has
    successfully constructed the model (i.e. all field-level validation
    has already passed).
    """

    def __init__(self) -> None:
        self._validators: dict[type[BaseModel], list[ValidatorFn]] = {}

    def register(
        self,
        model_type: type[ModelT],
    ) -> Callable[[ValidatorFn], ValidatorFn]:
        """Decorator to register a validator for *model_type*.

        Args:
            model_type: The Pydantic model class this validator applies to.

        Returns:
            Decorator function.

        Example::

            @registry.register(Neo4jConfig)
            def check_neo4j(config: Neo4jConfig, env: Environment) -> None:
                ...
        """

        def decorator(fn: ValidatorFn) -> ValidatorFn:
            self._validators.setdefault(model_type, []).append(fn)
            return fn

        return decorator

    def validate(self, config: BaseModel, env: Environment) -> None:
        """Run all validators registered for *config*'s type.

        Args:
            config: The configuration model instance to validate.
            env: Active deployment environment (passed to each validator).

        Raises:
            ConfigValidationError: If any validator raises.
        """
        for fn in self._validators.get(type(config), []):
            fn(config, env)

    def validate_all(self, root: BaseModel, env: Environment) -> None:
        """Validate all fields of *root* that have registered validators.

        Iterates over every field value of the root config and runs any
        registered validators for that field's model type.

        Args:
            root: The :class:`~infrastructure.config.models.root.RootConfig` instance.
            env: Active deployment environment.

        Raises:
            ConfigValidationError: On the first validation failure.
        """
        for field_value in root.__dict__.values():
            if isinstance(field_value, BaseModel):
                self.validate(field_value, env)


# ---------------------------------------------------------------------------
# Built-in validators
# ---------------------------------------------------------------------------

#: Shared validation registry used by bootstrap.
default_registry = ValidationRegistry()


@default_registry.register(  # type: ignore[arg-type]
    __import__(
        "infrastructure.config.models.neo4j",
        fromlist=["Neo4jConfig"],
    ).Neo4jConfig
)
def _validate_neo4j_password_in_prod(config: Any, env: Environment) -> None:  # noqa: ANN401
    """Require a non-empty Neo4j password in production."""
    if env.is_production and not config.auth.password:
        raise ConfigValidationError(
            section="neo4j",
            details="NEO4J password must be set in production (NEO4J_AUTH__PASSWORD).",
        )


@default_registry.register(  # type: ignore[arg-type]
    __import__(
        "infrastructure.config.models.security",
        fromlist=["SecurityConfig"],
    ).SecurityConfig
)
def _validate_jwt_secret_in_prod(config: Any, env: Environment) -> None:  # noqa: ANN401
    """Require a JWT secret key in production when JWT auth is active."""
    from infrastructure.config.models.security import AuthScheme

    if env.is_production and config.scheme == AuthScheme.JWT and not config.jwt.secret_key:
        raise ConfigValidationError(
            section="security",
            details="JWT secret_key must be set in production.",
        )
