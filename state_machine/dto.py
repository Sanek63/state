from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
class DecisionDTO(str, Enum):
    YES = "YES"
    NO = "NO"
    DEFAULT = "DEFAULT"


@dataclass(slots=True)
class TriggerContextDTO:
    """Marker base for workflow contexts.

    The engine expects a shared base type for all context DTOs,
    while concrete workflows define their own strongly-typed fields via subclassing.
    """

    pass


@dataclass(slots=True)
class TriggerExecutionDTO:
    decision: DecisionDTO


@dataclass(slots=True)
class TriggerRoutesDTO:
    yes: str | None = None
    no: str | None = None
    default: str | None = None

    def resolve_next(self, decision: DecisionDTO) -> str | None:
        if decision == DecisionDTO.YES:
            return self.yes or self.default
        if decision == DecisionDTO.NO:
            return self.no or self.default
        if decision == DecisionDTO.DEFAULT:
            return self.default
        raise ValueError(f"Unsupported decision value: {decision}")


@dataclass(slots=True)
class TriggerNodeDTO:
    name: str
    trigger_key: str
    routes: TriggerRoutesDTO = field(default_factory=TriggerRoutesDTO)


@dataclass(slots=True)
class WorkflowDTO:
    start_node: str
    nodes: dict[str, TriggerNodeDTO]

    def validate(self) -> None:
        if self.start_node not in self.nodes:
            raise ValueError(f"Start node '{self.start_node}' not found in workflow nodes")

        for node_name, node in self.nodes.items():
            if node.name != node_name:
                raise ValueError(
                    f"Node key '{node_name}' must match TriggerNodeDTO.name '{node.name}'"
                )
            for next_node in (node.routes.yes, node.routes.no, node.routes.default):
                if next_node is not None and next_node not in self.nodes:
                    raise ValueError(
                        f"Node '{node_name}' points to unknown next node '{next_node}'"
                    )
