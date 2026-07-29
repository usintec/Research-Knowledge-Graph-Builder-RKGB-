"""Pipeline stage contracts — abstract base classes for all pipeline stages.

Every pipeline stage must implement the ``PipelineStage`` ABC defined
in this package. Stages are responsible for orchestration only; they
dispatch commands and queries but never access repositories directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PipelineStage(ABC):
    """Abstract base class for all RKGB pipeline stages.

    A stage encapsulates a single, focused unit of pipeline orchestration.
    It receives a context object, performs its work (typically by dispatching
    commands or queries), and returns control to the pipeline runtime.

    Subclasses must implement ``execute``.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name identifying this stage within its pipeline.

        Returns:
            Stage name string.
        """

    @abstractmethod
    async def execute(self, context: Any) -> None:  # noqa: ANN401
        """Execute the stage with the given pipeline context.

        Args:
            context: The pipeline execution context carrying shared state.
        """
