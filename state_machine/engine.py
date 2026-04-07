from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from transitions import Machine
from transitions.extensions import GraphMachine

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
        self._validate_trigger_factories()
        self._model = WorkflowModel()
        self._machine = Machine(
            model=self._model,
            states=list(workflow.nodes.keys()),
            initial=workflow.start_node,
            auto_transitions=False,
        )
        self._register_transitions(self._machine)

    @property
    def current_node(self) -> str:
        return self._model.state

    def reset(self) -> None:
        self._model.state = self._workflow.start_node

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

    def get_graph(self, use_pygraphviz: bool = False) -> Any:
        graph_engine = "graphviz" if use_pygraphviz else "mermaid"
        graph_machine = GraphMachine(
            states=list(self._workflow.nodes.keys()),
            initial=self._workflow.start_node,
            auto_transitions=False,
            graph_engine=graph_engine,
        )
        self._register_transitions(graph_machine)
        graph_machine.machine_attributes["rankdir"] = "TB"
        return graph_machine.get_graph()

    def _build_trigger(self, trigger_key: str, options: dict) -> BaseTrigger:
        factory = self._trigger_factories.get(trigger_key)
        if not factory:
            raise KeyError(
                f"Missing trigger factory for key '{trigger_key}'. "
                "This should have been caught during workflow initialization."
            )
        return factory(options)

    def _validate_trigger_factories(self) -> None:
        used_trigger_keys = {node.trigger_key for node in self._workflow.nodes.values()}
        missing = sorted(used_trigger_keys - set(self._trigger_factories.keys()))
        if missing:
            raise KeyError(
                "Missing trigger factories for keys: " + ", ".join(f"'{key}'" for key in missing)
            )

    def _register_transitions(self, machine: Machine) -> None:
        for node in self._workflow.nodes.values():
            destinations = {
                route
                for route in (node.routes.yes, node.routes.no, node.routes.default)
                if route is not None
            }
            for next_node in destinations:
                machine.add_transition(
                    trigger=self._transition_name(node.name, next_node),
                    source=node.name,
                    dest=next_node,
                )

    @staticmethod
    def _transition_name(source: str, dest: str) -> str:
        return f"go__{source}__{dest}"
