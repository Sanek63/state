from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from .dto import DecisionDTO, TriggerContextDTO, TriggerExecutionDTO


class BaseTrigger(ABC):
    name: ClassVar[str] = "Trigger"
    doc: ClassVar[str] = ""

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if "name" not in cls.__dict__:
            cls.name = cls.__name__.removesuffix("Trigger")
        if "doc" not in cls.__dict__:
            cls.doc = (cls.__doc__ or cls.__name__).strip()

    @abstractmethod
    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        pass


class AlwaysYesTrigger(BaseTrigger):
    name: ClassVar[str] = "Always YES"
    doc: ClassVar[str] = "Always returns YES decision."

    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.YES)


class AlwaysNoTrigger(BaseTrigger):
    name: ClassVar[str] = "Always NO"
    doc: ClassVar[str] = "Always returns NO decision."

    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.NO)


class ContainsKeyTrigger(BaseTrigger):
    name: ClassVar[str] = "Contains key"
    doc: ClassVar[str] = "Returns YES when required context attribute exists."

    def __init__(self, required_key: str) -> None:
        self.required_key = required_key

    def execute(self, context: TriggerContextDTO) -> TriggerExecutionDTO:
        decision = (
            DecisionDTO.YES
            if getattr(context, self.required_key, None) is not None
            else DecisionDTO.NO
        )
        return TriggerExecutionDTO(decision=decision)
