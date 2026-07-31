# Dependency Injection Framework

## Overview

RKGB uses a custom, interface-first Dependency Injection (DI) framework built on SOLID and Clean Architecture principles. The framework enforces:

- **Constructor injection only** — dependencies are declared in `__init__` and received automatically.
- **Explicit dependency graphs** — every dependency appears in type annotations; nothing is hidden.
- **Fail-fast startup validation** — registration problems are caught at boot time, not at runtime.
- **Lifetime management** — singleton, scoped, and transient lifetimes are enforced by the container.

---

## Architecture

```
bootstrap_container()
        │
        ▼
CompositionRoot
        │  applies modules in order
        ├─ ConfigurationModule  (ConfigManager + config sections)
        ├─ LoggingModule        (LoggingManager + LoggerFactory)
        ├─ RepositoryModule     (domain repositories — Step A5+)
        ├─ ProcessingModule     (pipeline engine — Step B+)
        ├─ ApplicationModule    (CQRS buses — Step A5+)
        ├─ PipelineModule       (pipeline DSL — Step B+)
        ├─ PluginModule         (plugin registry)
        └─ [extra_modules ...]  (caller-supplied overrides / plugins)
        │
        ▼
    DIContainer
        │  build()
        ▼
ServiceProvider  ←─── root (owns singleton cache)
        │  create_scope()
        ▼
  ServiceScope
        │
        ▼
ServiceProvider  ←─── scoped (shares singletons, owns scoped cache)
```

---

## Key Components

### `ServiceLifetime`

Three lifetimes are supported:

| Lifetime | Description | Examples |
|----------|-------------|---------|
| `SINGLETON` | One instance per application process | `ConfigManager`, `LoggingManager`, `CommandBus` |
| `SCOPED` | One instance per execution scope | `PipelineContext`, `RequestContext` |
| `TRANSIENT` | New instance on every resolution | `CommandHandlers`, `Validators`, `Policies` |

### `ServiceCollection`

The *registration* phase. Describes what to build without constructing anything.

```python
from infrastructure.dependency_injection.service_collection import ServiceCollection

services = ServiceCollection()
services.add_singleton(IRepository, Neo4jDocumentRepository)
services.add_transient(IValidator, DocumentValidator)
services.add_scoped(PipelineContext)
```

Fluent API — all methods return `self` for chaining:

```python
services \
    .add_singleton(ConfigManager, instance=config_manager) \
    .add_singleton(LoggerFactory, factory=lambda p: p.resolve(LoggingManager).factory) \
    .add_transient(IValidator, DocumentValidator)
```

### `ServiceProvider`

The *resolution* phase. Constructs and manages service instances.

```python
provider = services.build_provider()
repo = provider.resolve(IRepository)
```

The provider automatically inspects constructor parameters and resolves typed dependencies recursively. Parameters with defaults are skipped when their type is unregistered; parameters without defaults and without registrations raise `ServiceResolutionError`.

### `DIContainer`

Combines registration and build in one convenient API:

```python
from infrastructure.dependency_injection.container import DIContainer

container = DIContainer()
container.add_singleton(ILogger, StructLogger)
container.add_module(RepositoryModule())
provider = container.build()
```

---

## Object Lifecycle

### Singleton

```
First resolve(ICommandBus)
    → build() called → instance stored in _singletons
    → return instance

Second resolve(ICommandBus)
    → found in _singletons
    → return same instance (no construction)
```

### Scoped

```
provider.create_scope() → ServiceScope
    ├─ enter scope (via context manager or .provider property)
    ├─ resolve(PipelineContext) → build() → stored in _scoped_instances
    ├─ resolve(PipelineContext) again → returned from _scoped_instances
    └─ exit scope → _scoped_instances.clear()

resolve(PipelineContext) on root provider (not in scope)
    → raises ScopeError
```

### Transient

```
resolve(IValidator)
    → build() called → instance returned
    → no caching

resolve(IValidator) again
    → build() called again → new instance returned
```

---

## Service Lifetimes — Registration Reference

```python
# Singleton — one instance for the application lifetime
services.add_singleton(ICommandBus, InMemoryCommandBus)

# Singleton — with a pre-built instance
services.add_singleton(ConfigManager, instance=config_manager)

# Singleton — with a factory (receives the active ServiceProvider)
services.add_singleton(
    LoggerFactory,
    factory=lambda provider: provider.resolve(LoggingManager).factory,
)

# Scoped — one per execution scope
services.add_scoped(PipelineContext)

# Transient — fresh instance on every resolve
services.add_transient(IValidator, DocumentValidator)
```

---

## Registration Process

### 1. Direct registration

```python
services.add_singleton(IRepository, Neo4jDocumentRepository)
#   ↑ abstract type       ↑ concrete type (constructor-injected)
```

### 2. Registration modules

Group related services into a module:

```python
class RepositoryModule:
    def register(self, services: IServiceCollection) -> None:
        services.add_singleton(IDocumentRepository, Neo4jDocumentRepository)
        services.add_singleton(IEntityRepository, Neo4jEntityRepository)

container.add_module(RepositoryModule())
```

### 3. Auto-discovery

Decorate classes with `@injectable` (or its shorthands) and let `ServiceDiscovery` find them:

```python
from infrastructure.dependency_injection.decorators import singleton, transient

@singleton(service_type=ICommandBus)
class InMemoryCommandBus:
    def __init__(self, logger: LoggerFactory) -> None: ...

@transient(service_type=IValidator)
class DocumentValidator:
    def __init__(self, repo: IDocumentRepository) -> None: ...
```

```python
from infrastructure.dependency_injection.discovery import ServiceDiscovery

discovery = ServiceDiscovery()
discovery.scan_package("application.command_handlers", services)
discovery.scan_package("application.validators", services)
```

---

## Constructor Injection

Constructor injection is the **only** injection style supported.

```python
# ✅ Correct — declare all dependencies in __init__
class ValidateDocumentHandler:
    def __init__(
        self,
        repository: IDocumentRepository,
        logger: LoggerFactory,
        config: ApplicationConfig,
    ) -> None:
        self._repository = repository
        self._logger = logger.get_logger("validate_document")
        self._config = config
```

```python
# ❌ Wrong — reaching into the container directly (Service Locator anti-pattern)
class ValidateDocumentHandler:
    def __init__(self, container: DIContainer) -> None:
        self._repo = container.resolve(IDocumentRepository)  # never do this
```

The provider inspects `__init__` parameter types and resolves each annotated parameter:

```
ValidateDocumentHandler.__init__
    repository: IDocumentRepository  →  resolve(IDocumentRepository)  →  Neo4jDocumentRepository
    logger: LoggerFactory             →  resolve(LoggerFactory)        →  LoggerFactory (singleton)
    config: ApplicationConfig         →  resolve(ApplicationConfig)    →  ApplicationConfig (singleton)
```

---

## Scope Management

Create a scope for each isolated execution context:

```python
# HTTP request scope (future)
with provider.create_scope() as request_provider:
    handler = request_provider.resolve(ICommandHandler)
    await handler.handle(command)
# Scope disposed; scoped instances discarded.

# Pipeline execution scope
with provider.create_scope() as pipeline_provider:
    ctx = pipeline_provider.resolve(PipelineContext)
    manager = pipeline_provider.resolve(IPipelineManager)
    await manager.run(pipeline_id, ctx)

# CLI execution scope
scope = provider.create_scope()
cli_provider = scope.provider
try:
    runner = cli_provider.resolve(CLICommandRunner)
    runner.execute(args)
finally:
    scope.__exit__(None, None, None)
```

Supported scope contexts:
| Context | Status |
|---------|--------|
| HTTP requests | Future (FastAPI middleware) |
| Pipeline execution | Planned (Step B+) |
| CLI execution | Planned |
| Scheduled jobs | Planned |
| Kafka messages | Planned |

---

## Composition Root

The `CompositionRoot` is the **only** place where concrete implementations are bound to their interfaces. All other modules receive their dependencies through constructor injection.

```python
from infrastructure.dependency_injection.composition_root import CompositionRoot

# Standard usage (called via bootstrap_container)
root = CompositionRoot(
    config_manager=config_manager,
    logging_manager=logging_manager,
    extra_modules=[MyFeatureModule()],   # optional
)
provider = root.build()
```

### Integration with Step A2 (Configuration)

`ConfigurationModule` receives the pre-built `ConfigManager` and registers it as a singleton. Every typed config section (e.g. `Neo4jConfig`, `LoggingConfig`) is registered with a factory that calls `manager.get(SectionType)` on first resolution — guaranteeing consistency with the loaded config.

```python
# How the config module registers sections:
services.add_singleton(
    Neo4jConfig,
    factory=lambda p: p.resolve(ConfigManager).get(Neo4jConfig),
)
```

### Integration with Step A3 (Logging)

`LoggingModule` receives the pre-built `LoggingManager` and registers both the manager and its `LoggerFactory` as singletons.

```python
services.add_singleton(LoggingManager, instance=logging_manager)
services.add_singleton(
    LoggerFactory,
    factory=lambda p: p.resolve(LoggingManager).factory,
)
```

Components that need a logger declare `LoggerFactory` as a constructor parameter — they never import structlog or the stdlib `logging` module directly.

### Integration with Step A5 (CQRS — future)

`ApplicationModule` reserves the CQRS bus slots. When Step A5 is implemented, replace the placeholder comments with:

```python
services.add_singleton(ICommandBus, InMemoryCommandBus)
services.add_singleton(IQueryBus, InMemoryQueryBus)
services.add_singleton(IEventBus, InMemoryEventBus)
```

Command and query handlers are registered as transient services via auto-discovery:

```python
discovery = ServiceDiscovery()
discovery.scan_package("application.command_handlers", services)
discovery.scan_package("application.query_handlers", services)
```

### Integration with the Processing Engine (Step B+)

`ProcessingModule` reserves slots for the Pipeline Manager, Stage Registry, and related infrastructure. Pipeline execution contexts will be scoped services — one per pipeline run.

### Integration with the Plugin Architecture

`PluginModule` reserves slots for the Plugin Registry. Plugins extend the platform by:
1. Implementing `IRegistrationModule.register()`.
2. Passing the module via `extra_modules` in `bootstrap_container()`.

```python
provider = bootstrap_container(
    config_manager,
    logging_manager,
    extra_modules=[MyPlugin().as_module()],
)
```

---

## Startup Validation

Call `validate_registrations()` (done automatically by `CompositionRoot.build()`) to surface problems at boot time:

| Check | What it detects |
|-------|----------------|
| Abstract implementation | A concrete type is abstract (cannot be instantiated) |
| Missing dependency | A required constructor parameter is not registered |
| Circular dependency | A → B → A dependency chain |
| Lifetime violation | A singleton depends directly on a scoped service |

```python
from infrastructure.dependency_injection.validators import validate_registrations

validate_registrations(services.registrations)
# Raises StartupValidationError listing ALL errors found, not just the first.
```

---

## Extension Points

### Adding services from application features

```python
class DocumentIngestionModule:
    def register(self, services: IServiceCollection) -> None:
        services.add_transient(IIngestCommand, IngestDocumentCommand)
        services.add_singleton(IIngestionPipeline, DocumentIngestionPipeline)

provider = bootstrap_container(
    config, logging,
    extra_modules=[DocumentIngestionModule()],
)
```

### Adding services from plugins

```python
provider = bootstrap_container(
    config, logging,
    extra_modules=[MyPlugin().build_module()],
)
```

### Test doubles

```python
from infrastructure.dependency_injection.bootstrap import build_test_container
from infrastructure.dependency_injection.service_collection import ServiceCollection

class FakeRepositoryModule:
    def register(self, services: ServiceCollection) -> None:
        services.add_singleton(IDocumentRepository, InMemoryDocumentRepository)

provider = build_test_container(extra_modules=[FakeRepositoryModule()])
handler = provider.resolve(ValidateDocumentHandler)
```

---

## Best Practices

1. **Declare all dependencies in `__init__`** — never reach into the container from business code.
2. **Depend on interfaces (Protocols/ABCs), not concrete types** — the container binds the concrete type.
3. **Use the shortest lifetime that satisfies correctness** — prefer transient for handlers; only use singletons for genuinely shared infrastructure.
4. **Never inject a scoped service into a singleton** — the startup validator will catch this.
5. **One registration module per concern** — keeps the composition root readable.
6. **Use `build_test_container()` in tests** — avoids production infrastructure, is fast and hermetic.
7. **Prefer `@singleton` / `@transient` decorators for auto-discovered classes** — reduces boilerplate in registration modules.
8. **Factory registrations are powerful but opaque** — document what the factory produces and why a factory is needed.

---

## API Reference

### `bootstrap_container(config_manager, logging_manager, extra_modules?, skip_validation?)`
Single startup entry point. Returns the root `ServiceProvider`.

### `build_test_container(config_manager?, logging_manager?, extra_modules?)`
Builds a hermetic container for unit tests. Validation is skipped.

### `ServiceCollection`
| Method | Description |
|--------|-------------|
| `add_singleton(svc, impl?, *, factory?, instance?, replace?)` | Register a singleton |
| `add_scoped(svc, impl?, *, factory?, replace?)` | Register a scoped service |
| `add_transient(svc, impl?, *, factory?, replace?)` | Register a transient service |
| `add_module(module)` | Apply a registration module |
| `has_registration(type)` | Check if a type is registered |
| `build_provider()` | Build a `ServiceProvider` |

### `ServiceProvider`
| Method | Description |
|--------|-------------|
| `resolve(type)` | Resolve a service (raises on missing) |
| `try_resolve(type)` | Resolve, returning `None` if unregistered |
| `create_scope()` | Create a `ServiceScope` |

### Decorators
| Decorator | Equivalent |
|-----------|-----------|
| `@singleton(service_type?)` | `@injectable(SINGLETON, service_type?)` |
| `@scoped(service_type?)` | `@injectable(SCOPED, service_type?)` |
| `@transient(service_type?)` | `@injectable(TRANSIENT, service_type?)` |

### Exceptions
| Exception | When raised |
|-----------|-------------|
| `ServiceNotFoundError` | Type not registered |
| `CircularDependencyError` | Circular dependency detected |
| `DuplicateRegistrationError` | Type registered twice without `replace=True` |
| `ServiceResolutionError` | Construction raised an exception |
| `ScopeError` | Scoped service resolved outside a scope |
| `StartupValidationError` | `validate_registrations()` found errors |
