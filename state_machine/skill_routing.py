from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from punq import Container

from .dto import (
    DecisionDTO,
    TriggerContextDTO,
    TriggerExecutionDTO,
    TriggerNodeDTO,
    TriggerRoutesDTO,
    WorkflowDTO,
)
from .engine import StatefulWorkflow, TriggerFactory, WorkflowStepResultDTO
from .triggers import BaseTrigger


@dataclass(slots=True)
class SkillRoutingContextDTO(TriggerContextDTO):
    skill_json: list[dict[str, Any]] = field(default_factory=list)
    skill_num: int = 0
    skill_id: str | None = None
    wait_time: int = 0

    is_transfer: bool = False
    classification_skill_id: str | None = None
    route_default_skill_mapping: str | None = None
    twork_data_skill_id: str | None = None
    transfer_default_skill_id: str | None = None
    retransfer_default_skill_id: str | None = None

    skill_settings_received: bool = True
    numeric_identifier_present: bool = True
    skill_active: bool = True
    transfer_allowed: bool = True
    worktime_enabled: bool = True
    worktime_range_single_value: bool = False
    is_now_worktime: bool = True

    has_reserve_skill: bool = False
    reserve_skill_name: str | None = None
    reserve_skill_timeout: int = 0
    reserve_skill_found: bool = False
    reserve_skill_exists_in_skill_json: bool = True
    smart_ivr_id_skill: str | None = None


class InitSkillRunTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_json = []
        context.skill_num = 0
        context.wait_time = 0
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class IsTransferTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.is_transfer else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsClassificationSkillIdNullTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.classification_skill_id is None else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class ResolveSkillFromRouteDefaultTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_id = context.route_default_skill_mapping
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class IsTworkDataSkillIdNullTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.twork_data_skill_id is None else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class ResolveRetransferSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_id = context.retransfer_default_skill_id
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class IsTransferAfterTworkTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.is_transfer else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class ResolveTransferSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_id = context.transfer_default_skill_id
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class AppendRetransferSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_json.append(
            {
                "id": context.retransfer_default_skill_id,
                "key": "call_ui3_RETRANSFER_DEFAULT_SKILL_ID",
                "wait_time": 0,
            }
        )
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class AppendTransferSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_json.append(
            {
                "id": context.transfer_default_skill_id,
                "key": "call_ui3_TRANSFER_DEFAULT_SKILL_ID",
                "wait_time": 0,
            }
        )
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class GetSkillSettingsTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        if context.skill_id is None:
            context.skill_id = context.classification_skill_id
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class SkillSettingsReceivedTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.skill_settings_received else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class HasNumericIdentifierTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.numeric_identifier_present else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsSkillActiveTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.skill_active else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsTransferForbiddenTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if not context.transfer_allowed else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsWorktimeEnabledTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.worktime_enabled else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsWorktimeRangeSingleValueTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.worktime_range_single_value else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class IsNowWorktimeTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.is_now_worktime else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class HasReserveSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.has_reserve_skill else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class CurrentSkillNumIsZeroTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.skill_num == 0 else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class AppendCurrentSkillTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_json.append(
            {
                "id": context.skill_id,
                "key": context.skill_id,
                "wait_time": context.wait_time,
            }
        )
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class AppendCurrentSkillForReserveTrigger(AppendCurrentSkillTrigger):
    pass


class ReserveSkillInSkillJsonExistsTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = (
            DecisionDTO.YES if context.reserve_skill_exists_in_skill_json else DecisionDTO.NO
        )
        return TriggerExecutionDTO(decision=decision)


class IncrementWithReserveTimeoutTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_num += 1
        context.wait_time = context.reserve_skill_timeout
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class TakeReserveSkillFromSmartIvrTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_id = context.smart_ivr_id_skill
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class ReserveSkillFoundTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if context.reserve_skill_found else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class SetCurrentSkillToReserveTrigger(TakeReserveSkillFromSmartIvrTrigger):
    pass


class StubTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class FinishTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class SkillRoutingKeys:
    """Shared constants for both workflow node names and trigger registry keys."""

    INIT_SKILL_RUN = "init_skill_run"
    IS_TRANSFER = "is_transfer"
    CLASSIFICATION_SKILL_ID_IS_NULL = "classification_skill_id_is_null"
    RESOLVE_SKILL_FROM_ROUTE_DEFAULT = "resolve_skill_from_route_default"
    IS_TWORK_DATA_SKILL_ID_NULL = "is_twork_data_skill_id_null"
    RESOLVE_RETRANSFER_SKILL = "resolve_retransfer_skill"
    APPEND_RETRANSFER_SKILL = "append_retransfer_skill"
    IS_TRANSFER_AFTER_TWORK = "is_transfer_after_twork"
    RESOLVE_TRANSFER_SKILL = "resolve_transfer_skill"
    APPEND_TRANSFER_SKILL = "append_transfer_skill"
    GET_SKILL_SETTINGS = "get_skill_settings"
    SKILL_SETTINGS_RECEIVED = "skill_settings_received"
    HAS_NUMERIC_IDENTIFIER = "has_numeric_identifier"
    SKILL_ACTIVE = "skill_active"
    IS_TRANSFER_FORBIDDEN = "is_transfer_forbidden"
    WORKTIME_ENABLED = "worktime_enabled"
    WORKTIME_RANGE_SINGLE_VALUE = "worktime_range_single_value"
    IS_NOW_WORKTIME = "is_now_worktime"
    HAS_RESERVE_SKILL = "has_reserve_skill"
    APPEND_CURRENT_SKILL_FOR_RESERVE = "append_current_skill_for_reserve"
    RESERVE_SKILL_IN_SKILL_JSON_EXISTS = "reserve_skill_in_skill_json_exists"
    INCREMENT_WITH_RESERVE_TIMEOUT = "increment_with_reserve_timeout"
    TAKE_RESERVE_SKILL_FROM_SMART_IVR = "take_reserve_skill_from_smart_ivr"
    RESERVE_SKILL_FOUND = "reserve_skill_found"
    SET_CURRENT_SKILL_TO_RESERVE = "set_current_skill_to_reserve"
    STUB = "stub"
    CURRENT_SKILL_NUM_IS_ZERO = "current_skill_num_is_zero"
    APPEND_CURRENT_SKILL = "append_current_skill"
    FINISH = "finish"
    FINISH_NO_RESERVE = "finish_no_reserve"


SKILL_ROUTING_TERMINAL_STATES = frozenset(
    {SkillRoutingKeys.FINISH, SkillRoutingKeys.FINISH_NO_RESERVE}
)


@dataclass(frozen=True, slots=True)
class SkillRoutingNodeConfig:
    trigger_key: str
    trigger_type: type[BaseTrigger]
    trigger_name: str | None = None
    trigger_doc: str | None = None
    routes: TriggerRoutesDTO = field(default_factory=TriggerRoutesDTO)


@dataclass(frozen=True, slots=True)
class SkillRoutingMachineConfig:
    initial_state: str
    terminal_states: frozenset[str]
    node_configs: dict[str, SkillRoutingNodeConfig]


@dataclass(slots=True)
class MachineState:
    state_machine: StatefulWorkflow

    @property
    def current_node(self) -> str:
        return self.state_machine.current_node

    def reset(self) -> None:
        self.state_machine.reset()

    def run(
        self,
        context: TriggerContextDTO,
        max_steps: int = 100,
    ) -> list[WorkflowStepResultDTO]:
        return self.state_machine.run(context=context, max_steps=max_steps)

    def run_and_get_result(
        self,
        context: SkillRoutingContextDTO,
        max_steps: int = 100,
    ) -> SkillRoutingContextDTO:
        self.state_machine.run(context=context, max_steps=max_steps)
        return context


def _build_skill_routing_node_configs() -> dict[str, SkillRoutingNodeConfig]:
    n = SkillRoutingKeys

    def node_config(
        trigger_key: str,
        trigger_cls: type[BaseTrigger],
        routes: TriggerRoutesDTO,
    ) -> SkillRoutingNodeConfig:
        return SkillRoutingNodeConfig(
            trigger_key=trigger_key,
            trigger_type=trigger_cls,
            trigger_name=trigger_cls.name,
            trigger_doc=trigger_cls.doc,
            routes=routes,
        )

    return {
        n.INIT_SKILL_RUN: node_config(
            trigger_key=n.INIT_SKILL_RUN,
            trigger_cls=InitSkillRunTrigger,
            routes=TriggerRoutesDTO(default=n.IS_TRANSFER),
        ),
        n.IS_TRANSFER: node_config(
            trigger_key=n.IS_TRANSFER,
            trigger_cls=IsTransferTrigger,
            routes=TriggerRoutesDTO(
                yes=n.CLASSIFICATION_SKILL_ID_IS_NULL,
                no=n.IS_TWORK_DATA_SKILL_ID_NULL,
            ),
        ),
        n.CLASSIFICATION_SKILL_ID_IS_NULL: node_config(
            trigger_key=n.CLASSIFICATION_SKILL_ID_IS_NULL,
            trigger_cls=IsClassificationSkillIdNullTrigger,
            routes=TriggerRoutesDTO(
                yes=n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
                no=n.GET_SKILL_SETTINGS,
            ),
        ),
        n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT: node_config(
            trigger_key=n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
            trigger_cls=ResolveSkillFromRouteDefaultTrigger,
            routes=TriggerRoutesDTO(default=n.GET_SKILL_SETTINGS),
        ),
        n.IS_TWORK_DATA_SKILL_ID_NULL: node_config(
            trigger_key=n.IS_TWORK_DATA_SKILL_ID_NULL,
            trigger_cls=IsTworkDataSkillIdNullTrigger,
            routes=TriggerRoutesDTO(
                yes=n.RESOLVE_RETRANSFER_SKILL,
                no=n.IS_TRANSFER_AFTER_TWORK,
            ),
        ),
        n.RESOLVE_RETRANSFER_SKILL: node_config(
            trigger_key=n.RESOLVE_RETRANSFER_SKILL,
            trigger_cls=ResolveRetransferSkillTrigger,
            routes=TriggerRoutesDTO(default=n.APPEND_RETRANSFER_SKILL),
        ),
        n.APPEND_RETRANSFER_SKILL: node_config(
            trigger_key=n.APPEND_RETRANSFER_SKILL,
            trigger_cls=AppendRetransferSkillTrigger,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.IS_TRANSFER_AFTER_TWORK: node_config(
            trigger_key=n.IS_TRANSFER_AFTER_TWORK,
            trigger_cls=IsTransferAfterTworkTrigger,
            routes=TriggerRoutesDTO(yes=n.RESOLVE_TRANSFER_SKILL, no=n.GET_SKILL_SETTINGS),
        ),
        n.RESOLVE_TRANSFER_SKILL: node_config(
            trigger_key=n.RESOLVE_TRANSFER_SKILL,
            trigger_cls=ResolveTransferSkillTrigger,
            routes=TriggerRoutesDTO(default=n.APPEND_TRANSFER_SKILL),
        ),
        n.APPEND_TRANSFER_SKILL: node_config(
            trigger_key=n.APPEND_TRANSFER_SKILL,
            trigger_cls=AppendTransferSkillTrigger,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.GET_SKILL_SETTINGS: node_config(
            trigger_key=n.GET_SKILL_SETTINGS,
            trigger_cls=GetSkillSettingsTrigger,
            routes=TriggerRoutesDTO(default=n.SKILL_SETTINGS_RECEIVED),
        ),
        n.SKILL_SETTINGS_RECEIVED: node_config(
            trigger_key=n.SKILL_SETTINGS_RECEIVED,
            trigger_cls=SkillSettingsReceivedTrigger,
            routes=TriggerRoutesDTO(yes=n.HAS_NUMERIC_IDENTIFIER, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.HAS_NUMERIC_IDENTIFIER: node_config(
            trigger_key=n.HAS_NUMERIC_IDENTIFIER,
            trigger_cls=HasNumericIdentifierTrigger,
            routes=TriggerRoutesDTO(yes=n.SKILL_ACTIVE, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.SKILL_ACTIVE: node_config(
            trigger_key=n.SKILL_ACTIVE,
            trigger_cls=IsSkillActiveTrigger,
            routes=TriggerRoutesDTO(yes=n.IS_TRANSFER_FORBIDDEN, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.IS_TRANSFER_FORBIDDEN: node_config(
            trigger_key=n.IS_TRANSFER_FORBIDDEN,
            trigger_cls=IsTransferForbiddenTrigger,
            routes=TriggerRoutesDTO(yes=n.WORKTIME_ENABLED, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.WORKTIME_ENABLED: node_config(
            trigger_key=n.WORKTIME_ENABLED,
            trigger_cls=IsWorktimeEnabledTrigger,
            routes=TriggerRoutesDTO(yes=n.WORKTIME_RANGE_SINGLE_VALUE, no=n.APPEND_CURRENT_SKILL),
        ),
        n.WORKTIME_RANGE_SINGLE_VALUE: node_config(
            trigger_key=n.WORKTIME_RANGE_SINGLE_VALUE,
            trigger_cls=IsWorktimeRangeSingleValueTrigger,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.IS_NOW_WORKTIME),
        ),
        n.IS_NOW_WORKTIME: node_config(
            trigger_key=n.IS_NOW_WORKTIME,
            trigger_cls=IsNowWorktimeTrigger,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.HAS_RESERVE_SKILL),
        ),
        n.HAS_RESERVE_SKILL: node_config(
            trigger_key=n.HAS_RESERVE_SKILL,
            trigger_cls=HasReserveSkillTrigger,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL_FOR_RESERVE, no=n.STUB),
        ),
        n.APPEND_CURRENT_SKILL_FOR_RESERVE: node_config(
            trigger_key=n.APPEND_CURRENT_SKILL_FOR_RESERVE,
            trigger_cls=AppendCurrentSkillForReserveTrigger,
            routes=TriggerRoutesDTO(default=n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS),
        ),
        n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS: node_config(
            trigger_key=n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS,
            trigger_cls=ReserveSkillInSkillJsonExistsTrigger,
            routes=TriggerRoutesDTO(yes=n.INCREMENT_WITH_RESERVE_TIMEOUT, no=n.FINISH_NO_RESERVE),
        ),
        n.INCREMENT_WITH_RESERVE_TIMEOUT: node_config(
            trigger_key=n.INCREMENT_WITH_RESERVE_TIMEOUT,
            trigger_cls=IncrementWithReserveTimeoutTrigger,
            routes=TriggerRoutesDTO(default=n.TAKE_RESERVE_SKILL_FROM_SMART_IVR),
        ),
        n.TAKE_RESERVE_SKILL_FROM_SMART_IVR: node_config(
            trigger_key=n.TAKE_RESERVE_SKILL_FROM_SMART_IVR,
            trigger_cls=TakeReserveSkillFromSmartIvrTrigger,
            routes=TriggerRoutesDTO(default=n.RESERVE_SKILL_FOUND),
        ),
        n.RESERVE_SKILL_FOUND: node_config(
            trigger_key=n.RESERVE_SKILL_FOUND,
            trigger_cls=ReserveSkillFoundTrigger,
            routes=TriggerRoutesDTO(yes=n.SET_CURRENT_SKILL_TO_RESERVE, no=n.FINISH_NO_RESERVE),
        ),
        n.SET_CURRENT_SKILL_TO_RESERVE: node_config(
            trigger_key=n.SET_CURRENT_SKILL_TO_RESERVE,
            trigger_cls=SetCurrentSkillToReserveTrigger,
            routes=TriggerRoutesDTO(default=n.APPEND_CURRENT_SKILL),
        ),
        n.STUB: node_config(
            trigger_key=n.STUB,
            trigger_cls=StubTrigger,
            routes=TriggerRoutesDTO(default=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.CURRENT_SKILL_NUM_IS_ZERO: node_config(
            trigger_key=n.CURRENT_SKILL_NUM_IS_ZERO,
            trigger_cls=CurrentSkillNumIsZeroTrigger,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.FINISH_NO_RESERVE),
        ),
        n.APPEND_CURRENT_SKILL: node_config(
            trigger_key=n.APPEND_CURRENT_SKILL,
            trigger_cls=AppendCurrentSkillTrigger,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.FINISH: node_config(
            trigger_key=n.FINISH,
            trigger_cls=FinishTrigger,
            routes=TriggerRoutesDTO(),
        ),
        n.FINISH_NO_RESERVE: node_config(
            trigger_key=n.FINISH,
            trigger_cls=FinishTrigger,
            routes=TriggerRoutesDTO(),
        ),
    }


def _validate_no_skill_routing_cycles(workflow: WorkflowDTO) -> None:
    visited: set[str] = set()
    recursion_stack: set[str] = set()
    path: list[str] = []

    def walk(node_name: str) -> None:
        if node_name in recursion_stack:
            cycle_start = path.index(node_name)
            cycle_path = " -> ".join(path[cycle_start:] + [node_name])
            raise ValueError(f"Detected cycle in skill routing workflow: {cycle_path}")
        if node_name in visited:
            return

        recursion_stack.add(node_name)
        path.append(node_name)
        node = workflow.nodes[node_name]
        next_nodes: list[str] = []
        seen_next_nodes: set[str] = set()
        for route in (node.routes.yes, node.routes.no, node.routes.default):
            if route is None or route in seen_next_nodes:
                continue
            seen_next_nodes.add(route)
            next_nodes.append(route)
        for next_node in next_nodes:
            walk(next_node)

        path.pop()
        recursion_stack.remove(node_name)
        visited.add(node_name)

    walk(workflow.start_node)


def _validate_terminal_states(workflow: WorkflowDTO, terminal_states: frozenset[str]) -> None:
    missing = sorted(terminal_states - set(workflow.nodes.keys()))
    if missing:
        raise ValueError(
            "Missing terminal states in skill routing workflow: "
            + ", ".join(f"'{state}'" for state in missing)
        )

    for terminal_state in terminal_states:
        routes = workflow.nodes[terminal_state].routes
        if any(route is not None for route in (routes.yes, routes.no, routes.default)):
            raise ValueError(f"Terminal state '{terminal_state}' must not have outgoing routes")


class SkillRoutingStateMachineFactory:
    def __init__(self, route_overrides: dict[str, TriggerRoutesDTO] | None = None) -> None:
        self._route_overrides = route_overrides

    def create(self) -> MachineState:
        config = self._build_config()
        trigger_types = self._build_registered_trigger_types(config)
        container = self._build_trigger_container(trigger_types)
        state_machine = StatefulWorkflow(
            workflow=self._build_workflow(config),
            trigger_factories=self._build_trigger_factories(
                container=container,
                trigger_types=trigger_types,
            ),
        )
        return MachineState(state_machine=state_machine)

    def create_workflow(self) -> WorkflowDTO:
        config = self._build_config()
        return self._build_workflow(config)

    def create_trigger_factories(self) -> dict[str, TriggerFactory]:
        config = self._build_config()
        trigger_types = self._build_registered_trigger_types(config)
        container = self._build_trigger_container(trigger_types)
        return self._build_trigger_factories(
            container=container,
            trigger_types=trigger_types,
        )

    def _build_config(self) -> SkillRoutingMachineConfig:
        node_configs = _build_skill_routing_node_configs()
        if self._route_overrides:
            for node_name, routes in self._route_overrides.items():
                if node_name not in node_configs:
                    raise KeyError(f"Unknown node for route override: '{node_name}'")
                config = node_configs[node_name]
                node_configs[node_name] = SkillRoutingNodeConfig(
                    trigger_key=config.trigger_key,
                    trigger_type=config.trigger_type,
                    trigger_name=config.trigger_name,
                    trigger_doc=config.trigger_doc,
                    routes=routes,
                )
        return SkillRoutingMachineConfig(
            initial_state=SkillRoutingKeys.INIT_SKILL_RUN,
            terminal_states=SKILL_ROUTING_TERMINAL_STATES,
            node_configs=node_configs,
        )

    @staticmethod
    def _build_workflow(config: SkillRoutingMachineConfig) -> WorkflowDTO:
        nodes = {
            node_name: TriggerNodeDTO(
                name=node_name,
                trigger_key=node_config.trigger_key,
                trigger_name=node_config.trigger_name,
                trigger_doc=node_config.trigger_doc,
                routes=node_config.routes,
            )
            for node_name, node_config in config.node_configs.items()
        }
        workflow = WorkflowDTO(start_node=config.initial_state, nodes=nodes)
        _validate_terminal_states(workflow, config.terminal_states)
        _validate_no_skill_routing_cycles(workflow)
        return workflow

    def _build_trigger_container(self, trigger_types: dict[str, type[BaseTrigger]]) -> Container:
        container = Container()
        for trigger_type in trigger_types.values():
            container.register(
                trigger_type,
                factory=lambda trigger_type=trigger_type: trigger_type(),
            )
        return container

    @staticmethod
    def _build_registered_trigger_types(
        config: SkillRoutingMachineConfig,
    ) -> dict[str, type[BaseTrigger]]:
        trigger_types: dict[str, type[BaseTrigger]] = {}
        for node_config in config.node_configs.values():
            existing_type = trigger_types.get(node_config.trigger_key)
            if existing_type is not None and existing_type != node_config.trigger_type:
                raise ValueError(
                    f"Conflicting trigger types for key '{node_config.trigger_key}': "
                    f"{existing_type.__name__} vs {node_config.trigger_type.__name__}"
                )
            trigger_types[node_config.trigger_key] = node_config.trigger_type
        return trigger_types

    @staticmethod
    def _build_trigger_factories(
        container: Container,
        trigger_types: dict[str, type[BaseTrigger]],
    ) -> dict[str, TriggerFactory]:
        return {
            trigger_key: SkillRoutingStateMachineFactory._build_trigger_factory(
                container=container,
                trigger_type=trigger_type,
            )
            for trigger_key, trigger_type in trigger_types.items()
        }

    @staticmethod
    def _build_trigger_factory(
        container: Container,
        trigger_type: type[BaseTrigger],
    ) -> TriggerFactory:
        def factory() -> BaseTrigger:
            return container.resolve(trigger_type)

        return factory


def build_skill_routing_workflow(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> WorkflowDTO:
    return SkillRoutingStateMachineFactory(route_overrides=route_overrides).create_workflow()


def build_skill_routing_trigger_factories() -> dict[str, TriggerFactory]:
    return SkillRoutingStateMachineFactory().create_trigger_factories()


def build_skill_routing_state_machine(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> MachineState:
    return SkillRoutingStateMachineFactory(route_overrides=route_overrides).create()
