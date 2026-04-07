from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from transitions import Machine

from .dto import DecisionDTO, TriggerContextDTO, TriggerExecutionDTO, WorkflowDTO
from .triggers import BaseTrigger


TriggerFactory = Callable[[dict], BaseTrigger]


@dataclass(slots=True)
class WorkflowStepResultDTO:
    node: str
    decision: DecisionDTO
    next_node: str | None
    data: dict = field(default_factory=dict)


class WorkflowModel:
    state: str


class StatefulWorkflow:
    def __init__(
        self,
        workflow: WorkflowDTO,
        trigger_factories: dict[str, TriggerFactory],
    ) -> None:
        workflow.validate()
        self._workflow = workflow
        self._trigger_factories = trigger_factories
        self._model = WorkflowModel()
        self._machine = Machine(
            model=self._model,
            states=list(workflow.nodes.keys()),
            initial=workflow.start_node,
            auto_transitions=False,
        )
        self._register_transitions()

    @property
    def current_node(self) -> str:
        return self._model.state

    def step(self, context: TriggerContextDTO) -> WorkflowStepResultDTO:
        node = self._workflow.nodes[self._model.state]
        trigger = self._build_trigger(node.trigger_key, node.options)
        execution: TriggerExecutionDTO = trigger.execute(context)
        next_node = node.routes.resolve_next(execution.decision)

        if next_node:
            self._model.trigger(self._transition_name(node.name, next_node))

        return WorkflowStepResultDTO(
            node=node.name,
            decision=execution.decision,
            next_node=next_node,
            data=execution.data,
        )

    def run(
        self,
        context: TriggerContextDTO,
        max_steps: int = 100,
    ) -> list[WorkflowStepResultDTO]:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero")

        history: list[WorkflowStepResultDTO] = []
        for _ in range(max_steps):
            result = self.step(context)
            history.append(result)
            if result.next_node is None:
                break
        else:
            raise RuntimeError("Workflow reached max_steps limit without termination")

        return history

    def _build_trigger(self, trigger_key: str, options: dict) -> BaseTrigger:
        factory = self._trigger_factories.get(trigger_key)
        if not factory:
            raise KeyError(f"Trigger factory not found for key '{trigger_key}'")
        return factory(options)

    def _register_transitions(self) -> None:
        for node in self._workflow.nodes.values():
            for next_node in {
                node.routes.yes,
                node.routes.no,
                node.routes.default,
            }:
                if next_node is None:
                    continue
                self._machine.add_transition(
                    trigger=self._transition_name(node.name, next_node),
                    source=node.name,
                    dest=next_node,
                )

    @staticmethod
    def _transition_name(source: str, dest: str) -> str:
        return f"go__{source}__{dest}"
