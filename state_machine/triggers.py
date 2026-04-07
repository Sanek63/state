from __future__ import annotations

from abc import ABC, abstractmethod

from .dto import DecisionDTO, TriggerContextDTO, TriggerExecutionDTO


class BaseTrigger(ABC):
    @abstractmethod
    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        raise NotImplementedError


class AlwaysYesTrigger(BaseTrigger):
    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.YES)


class AlwaysNoTrigger(BaseTrigger):
    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.NO)


class ContainsKeyTrigger(BaseTrigger):
    def __init__(self, required_key: str) -> None:
        self.required_key = required_key

    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        decision = (
            DecisionDTO.YES
            if self.required_key in context.payload
            else DecisionDTO.NO
        )
        return TriggerExecutionDTO(
            decision=decision,
            data={"required_key": self.required_key},
        )
