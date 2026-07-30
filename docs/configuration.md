# RKGB — Configuration Framework

## Overview

The RKGB Configuration Framework is a centralized, strongly typed, environment-aware configuration system that follows Clean Architecture, Twelve-Factor App principles, and Dependency Inversion.

**No component reads `os.environ` directly.** All configuration flows through the `ConfigManager`.

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │        bootstrap_config()    │
                    └──────────────┬──────────────┘
                                   │ builds
                    ┌──────────────▼──────────────┐
                    │        ConfigManager         │
                    │  (one per application)       │
                    └──┬──────────────────────┬───┘
                       │                      │
              ┌────────▼──────┐    ┌──────────▼────────┐
              │ ConfigResolver │    │  ValidationRegistry│
              │ (merge & prec.)│    │  (cross-field)    │
              └────────┬──────┘    └───────────────────┘
                       │ sorted by priority
          ┌────────────┼──────────────┐
          ▼            ▼              ▼
   YAMLProvider   YAMLProvider  EnvProvider
   (base.yaml)   (dev.yaml)    (RKGB__*=)
   priority=20   priority=30   priority=40
```

### Key Components

| Component | File | Responsibility |
|---|---|---|
| `ConfigManager` | `manager.py` | Orchestrates load, merge, validate, cache |
| `ConfigResolver` | `resolver.py` | Priority-based deep merge of provider dicts |
| `ConfigRegistry` | `registry.py` | Maps section keys → model types |
| `ConfigProvider` | `interfaces.py` | ABC for all provider implementations |
| `ValidationRegistry` | `validators.py` | Cross-field, post-construction validators |
| `InMemoryConfigCache` | `cache.py` | Caches the resolved `RootConfig` |
| `bootstrap_config()` | `bootstrap.py` | Startup entry point |
| `Environment` | `environment.py` | Typed environment enum |

---

## Configuration Lifecycle

```
1. bootstrap_config(config_dir, env, overrides)
         │
         ▼
2. Detect Environment (APP_ENV env var → Environment enum)
         │
         ▼
3. Build Providers
   ├── YAMLProvider("configs/base.yaml", priority=20, optional=True)
   ├── YAMLProvider("configs/<env>.yaml", priority=30, optional=True)
   ├── EnvProvider(prefix="RKGB__", priority=40)
   └── RuntimeOverrideProvider(overrides, priority=50)  [if provided]
         │
         ▼
4. ConfigResolver.resolve()
   └── sort providers by priority → deep-merge dicts (low → high)
         │
         ▼
5. RootConfig.model_validate(merged_dict)
   └── Pydantic validates every field, type-coerces, applies field validators
         │
         ▼
6. ValidationRegistry.validate_all(root, env)
   └── Cross-field rules (e.g. "require password in production")
         │
         ▼
7. Cache RootConfig in InMemoryConfigCache
         │
         ▼
8. Return ConfigManager → register with DI container
```

---

## Provider Hierarchy

| Priority | Provider | Source |
|---|---|---|
| 10 | *(Pydantic defaults)* | Field default values in models |
| 20 | `YAMLProvider` | `configs/base.yaml` |
| 30 | `YAMLProvider` | `configs/<env>.yaml` |
| 40 | `EnvProvider` | OS environment variables (`RKGB__*`) |
| 50 | `RuntimeOverrideProvider` | Programmatic overrides (tests, CLI) |

Higher priority **wins** on conflict.  Nested dicts are merged recursively.

---

## Environment Variables

Variables must follow the pattern:

```
RKGB__<SECTION>__<KEY>=value
```

Double underscores (`__`) separate path levels.

### Examples

```bash
RKGB__NEO4J__URI=bolt://neo4j:7687
RKGB__NEO4J__AUTH__PASSWORD=secret
RKGB__APPLICATION__DEBUG=false
RKGB__APPLICATION__PORT=9000
RKGB__FEATURE_FLAGS__ENABLE_KAFKA=true
RKGB__LOGGING__LEVEL=INFO
RKGB__LOGGING__FORMAT=json
```

### Type Coercion

| Input string | Python type |
|---|---|
| `"true"` / `"1"` / `"yes"` | `True` |
| `"false"` / `"0"` / `"no"` | `False` |
| `"42"` | `int` |
| `"3.14"` | `float` |
| Anything else | `str` |

---

## Configuration Models

Each domain has its own model — avoid the "one giant settings class" anti-pattern.

| Model | Key | Description |
|---|---|---|
| `ApplicationConfig` | `application` | App metadata, host, port, debug |
| `FastAPIConfig` | `fastapi` | Docs, middleware, timeouts |
| `Neo4jConfig` | `neo4j` | URI, auth, pool, TLS, retry |
| `StorageConfig` | `storage` | Local / S3 / GCS backends |
| `LoggingConfig` | `logging` | Level, format, file sink, OTEL |
| `SecurityConfig` | `security` | Auth scheme, JWT, rate limiting |
| `MonitoringConfig` | `monitoring` | Prometheus, OTEL, health checks |
| `EventBusConfig` | `event_bus` | In-process or Kafka |
| `KafkaConfig` | `kafka` | Bootstrap servers, SSL, producer/consumer |
| `ProcessingEngineConfig` | `processing` | Pipeline runtime, workers |
| `PluginConfig` | `plugins` | Plugin discovery, scan paths |
| `AIModelsConfig` | `ai_models` | OpenAI, Anthropic, Ollama, etc. |
| `EmbeddingsConfig` | `embeddings` | Provider, dimension, batch size |
| `VectorStoreConfig` | `vector_store` | Qdrant, Chroma, Pinecone, FAISS |
| `FeatureFlagsConfig` | `feature_flags` | All platform feature toggles |
| `TestingConfig` | `testing` | Test-environment helpers |
| `DockerConfig` | `docker` | Container names, network |

All models use `ConfigDict(frozen=True)` — they are **immutable** after construction.

---

## Feature Flags

Feature flags control which capabilities are active at runtime.

```python
from infrastructure.config.models import FeatureFlagsConfig

flags: FeatureFlagsConfig = manager.get(FeatureFlagsConfig)

if flags.enable_graph_rag:
    # activate GraphRAG query engine
    ...
```

Enable a flag in YAML:

```yaml
# configs/production.yaml
feature_flags:
  enable_graph_rag: true
  enable_metrics: true
```

Or via env var:

```bash
RKGB__FEATURE_FLAGS__ENABLE_GRAPH_RAG=true
```

---

## Dependency Injection Usage

The config manager is designed to integrate cleanly with the Lagom DI container (Step A3):

```python
# infrastructure/dependency_injection/container.py (Step A3)
from lagom import Container
from infrastructure.config.bootstrap import bootstrap_config
from infrastructure.config.models import Neo4jConfig, FeatureFlagsConfig

manager = bootstrap_config()
container = Container()

# Register the manager itself
container.define(ConfigManager, lambda: manager)

# Register individual sections — components depend on the specific type
container.define(Neo4jConfig, lambda: manager.get(Neo4jConfig))
container.define(FeatureFlagsConfig, lambda: manager.get(FeatureFlagsConfig))
```

Components declare their dependency on the specific config type:

```python
class Neo4jRepository:
    def __init__(self, config: Neo4jConfig) -> None:
        self._uri = config.uri
        self._auth = (config.auth.username, config.auth.password)
```

No component ever imports `ConfigManager` directly — they receive the narrowest config type they need.

---

## Plugin Configuration

Plugins register their own configuration section during bootstrap:

```python
# In the plugin's __init__.py
from infrastructure.config.registry import ConfigRegistry
from my_plugin.config import MyPluginConfig

def register(registry: ConfigRegistry) -> None:
    registry.register(
        "my_plugin",
        MyPluginConfig,
        version="1.0",
        description="My plugin configuration",
    )
```

The plugin's YAML key must match the registered key:

```yaml
# configs/development.yaml
my_plugin:
  api_url: "https://my-plugin.example.com"
  timeout: 30
```

---

## Environment Management

```python
from infrastructure.config.environment import Environment

env = Environment.current()   # reads APP_ENV

env.is_production   # True for PRODUCTION and STAGING
env.is_development  # True for LOCAL, DEVELOPMENT, DOCKER
env.is_testing      # True for TESTING and CI
```

---

## Testing

Use `build_test_config()` for hermetic unit tests — no files read, no env vars required:

```python
from infrastructure.config.bootstrap import build_test_config

def test_something() -> None:
    root = build_test_config({"neo4j": {"database": "test_db"}})
    assert root.neo4j.database == "test_db"
```

Use `RuntimeOverrideProvider` for finer-grained control:

```python
from infrastructure.config.manager import ConfigManager
from infrastructure.config.providers.yaml_provider import RuntimeOverrideProvider

def make_manager(**overrides):
    return ConfigManager(
        providers=[RuntimeOverrideProvider(overrides=overrides, priority=50)],
        env=Environment.TESTING,
    )
```

---

## Best Practices

1. **Never read `os.environ` directly** — always go through `ConfigManager`.
2. **Inject the narrowest config type** — `Neo4jConfig`, not `RootConfig`.
3. **Keep secrets out of YAML files** — use environment variables for passwords, API keys.
4. **Use `build_test_config()` in tests** — never depend on real files or real env vars.
5. **Add new sections to `RootConfig`** — one field per domain model.
6. **Validate early, fail fast** — add cross-field validators to `ValidationRegistry` for production safety rules.
7. **Document every feature flag** — field docstrings in `FeatureFlagsConfig` are the single source of truth.
