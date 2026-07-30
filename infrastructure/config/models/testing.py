"""Testing environment configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TestingConfig(BaseModel):
    """Configuration specific to the testing environment.

    Provides convenience flags for controlling test behaviour without
    modifying production code paths.
    """

    model_config = ConfigDict(frozen=True)

    use_in_memory_storage: bool = True
    use_mock_ai_provider: bool = True
    use_mock_event_bus: bool = True
    neo4j_database: str = "rkgb_test"
    seed_data: bool = False
    fixture_dir: str = "./tests/fixtures/data"
    max_query_timeout_seconds: float = Field(default=5.0, gt=0)
