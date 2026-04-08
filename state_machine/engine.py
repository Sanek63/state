from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from transitions import Machine
from transitions.extensions import GraphMachine

from .dto import DecisionDTO, TriggerContextDTO, TriggerExecutionDTO, WorkflowDTO
from .triggers import BaseTrigger


TriggerFactory = Callable[[], BaseTrigger]
GraphTransition = tuple[str, str, str]


@dataclass(slots=True)
class WorkflowStepResultDTO:
    node: str
    decision: DecisionDTO
    next_node: str | None


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
        self._states = list(workflow.nodes.keys())
        self._transitions = self._build_transitions()
        self._model = WorkflowModel()
        self._machine = Machine(
            model=self._model,
            states=self._states,
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
        trigger = self._build_trigger(node.trigger_key)
        execution: TriggerExecutionDTO = trigger.execute(context)
        next_node = node.routes.resolve_next(execution.decision)

        if next_node:
            self._model.trigger(self._transition_name(node.name, next_node))

        return WorkflowStepResultDTO(
            node=node.name,
            decision=execution.decision,
            next_node=next_node,
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

    def get_graph(self, use_pygraphviz: bool = False):
        graph_engine = "graphviz" if use_pygraphviz else "mermaid"
        graph_machine = GraphMachine(
            states=self._states,
            initial=self._workflow.start_node,
            transitions=[list(transition) for transition in self._transitions],
            auto_transitions=False,
            graph_engine=graph_engine,
        )
        graph_machine.machine_attributes["rankdir"] = "TB"
        return graph_machine.get_graph()

    def _build_trigger(self, trigger_key: str) -> BaseTrigger:
        factory = self._trigger_factories.get(trigger_key)
        if not factory:
            raise KeyError(
                f"Missing trigger factory for key '{trigger_key}'. "
                "This should have been caught during workflow initialization."
            )
        return factory()

    def _validate_trigger_factories(self) -> None:
        used_trigger_keys = {node.trigger_key for node in self._workflow.nodes.values()}
        missing = sorted(used_trigger_keys - set(self._trigger_factories.keys()))
        if missing:
            raise KeyError(
                "Missing trigger factories for keys: " + ", ".join(f"'{key}'" for key in missing)
            )

    def _register_transitions(self, machine: Machine) -> None:
        for trigger, source, dest in self._transitions:
            machine.add_transition(trigger=trigger, source=source, dest=dest)

    def _build_transitions(self) -> tuple[GraphTransition, ...]:
        transitions: list[GraphTransition] = []
        for node in self._workflow.nodes.values():
            ordered_unique_destinations = dict.fromkeys(
                route
                for route in (node.routes.yes, node.routes.no)
                if route is not None
            )
            for next_node in ordered_unique_destinations:
                transitions.append((self._transition_name(node.name, next_node), node.name, next_node))
        return tuple(transitions)

    @staticmethod
    def _transition_name(source: str, dest: str) -> str:
        return f"go__{source}__{dest}"
