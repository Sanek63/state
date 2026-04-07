from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .dto import (
    DecisionDTO,
    TriggerContextDTO,
    TriggerExecutionDTO,
    TriggerNodeDTO,
    TriggerRoutesDTO,
    WorkflowDTO,
)
from .engine import StatefulWorkflow, TriggerFactory
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


class PredicateTrigger(BaseTrigger):
    def __init__(self, predicate: Callable[[SkillRoutingContextDTO], bool]) -> None:
        self._predicate = predicate

    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        decision = DecisionDTO.YES if self._predicate(context) else DecisionDTO.NO
        return TriggerExecutionDTO(decision=decision)


class DefaultActionTrigger(BaseTrigger):
    def __init__(self, action: Callable[[SkillRoutingContextDTO], None] | None = None) -> None:
        self._action = action

    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        if self._action is not None:
            self._action(context)
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class SkillRoutingKey:
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


def _append_skill(
    context: SkillRoutingContextDTO,
    skill_id: str | None,
    key: str | None,
    wait_time: int,
) -> None:
    context.skill_json.append(
        {
            "id": skill_id,
            "key": key,
            "wait_time": wait_time,
        }
    )


def _init_skill_run(context: SkillRoutingContextDTO) -> None:
    context.skill_json = []
    context.skill_num = 0
    context.wait_time = 0


def _set_route_default_skill(context: SkillRoutingContextDTO) -> None:
    context.skill_id = context.route_default_skill_mapping


def _set_retransfer_skill(context: SkillRoutingContextDTO) -> None:
    context.skill_id = context.retransfer_default_skill_id


def _set_transfer_skill(context: SkillRoutingContextDTO) -> None:
    context.skill_id = context.transfer_default_skill_id


def _fallback_to_classification_skill(context: SkillRoutingContextDTO) -> None:
    if context.skill_id is None:
        context.skill_id = context.classification_skill_id


def _append_retransfer_skill(context: SkillRoutingContextDTO) -> None:
    _append_skill(
        context,
        skill_id=context.retransfer_default_skill_id,
        key="call_ui3_RETRANSFER_DEFAULT_SKILL_ID",
        wait_time=0,
    )


def _append_transfer_skill(context: SkillRoutingContextDTO) -> None:
    _append_skill(
        context,
        skill_id=context.transfer_default_skill_id,
        key="call_ui3_TRANSFER_DEFAULT_SKILL_ID",
        wait_time=0,
    )


def _append_current_skill(context: SkillRoutingContextDTO) -> None:
    _append_skill(
        context,
        skill_id=context.skill_id,
        key=context.skill_id,
        wait_time=context.wait_time,
    )


def _increment_with_reserve_timeout(context: SkillRoutingContextDTO) -> None:
    context.skill_num += 1
    context.wait_time = context.reserve_skill_timeout


def _set_skill_from_smart_ivr(context: SkillRoutingContextDTO) -> None:
    context.skill_id = context.smart_ivr_id_skill


def build_skill_routing_workflow(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> WorkflowDTO:
    k = SkillRoutingKey
    nodes: dict[str, TriggerNodeDTO] = {
        k.INIT_SKILL_RUN: TriggerNodeDTO(
            name=k.INIT_SKILL_RUN,
            trigger_key=k.INIT_SKILL_RUN,
            routes=TriggerRoutesDTO(default=k.IS_TRANSFER),
        ),
        k.IS_TRANSFER: TriggerNodeDTO(
            name=k.IS_TRANSFER,
            trigger_key=k.IS_TRANSFER,
            routes=TriggerRoutesDTO(
                yes=k.CLASSIFICATION_SKILL_ID_IS_NULL,
                no=k.IS_TWORK_DATA_SKILL_ID_NULL,
            ),
        ),
        k.CLASSIFICATION_SKILL_ID_IS_NULL: TriggerNodeDTO(
            name=k.CLASSIFICATION_SKILL_ID_IS_NULL,
            trigger_key=k.CLASSIFICATION_SKILL_ID_IS_NULL,
            routes=TriggerRoutesDTO(
                yes=k.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
                no=k.GET_SKILL_SETTINGS,
            ),
        ),
        k.RESOLVE_SKILL_FROM_ROUTE_DEFAULT: TriggerNodeDTO(
            name=k.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
            trigger_key=k.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
            routes=TriggerRoutesDTO(default=k.GET_SKILL_SETTINGS),
        ),
        k.IS_TWORK_DATA_SKILL_ID_NULL: TriggerNodeDTO(
            name=k.IS_TWORK_DATA_SKILL_ID_NULL,
            trigger_key=k.IS_TWORK_DATA_SKILL_ID_NULL,
            routes=TriggerRoutesDTO(
                yes=k.RESOLVE_RETRANSFER_SKILL,
                no=k.IS_TRANSFER_AFTER_TWORK,
            ),
        ),
        k.RESOLVE_RETRANSFER_SKILL: TriggerNodeDTO(
            name=k.RESOLVE_RETRANSFER_SKILL,
            trigger_key=k.RESOLVE_RETRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=k.APPEND_RETRANSFER_SKILL),
        ),
        k.APPEND_RETRANSFER_SKILL: TriggerNodeDTO(
            name=k.APPEND_RETRANSFER_SKILL,
            trigger_key=k.APPEND_RETRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=k.FINISH),
        ),
        k.IS_TRANSFER_AFTER_TWORK: TriggerNodeDTO(
            name=k.IS_TRANSFER_AFTER_TWORK,
            trigger_key=k.IS_TRANSFER_AFTER_TWORK,
            routes=TriggerRoutesDTO(yes=k.RESOLVE_TRANSFER_SKILL, no=k.GET_SKILL_SETTINGS),
        ),
        k.RESOLVE_TRANSFER_SKILL: TriggerNodeDTO(
            name=k.RESOLVE_TRANSFER_SKILL,
            trigger_key=k.RESOLVE_TRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=k.APPEND_TRANSFER_SKILL),
        ),
        k.APPEND_TRANSFER_SKILL: TriggerNodeDTO(
            name=k.APPEND_TRANSFER_SKILL,
            trigger_key=k.APPEND_TRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=k.FINISH),
        ),
        k.GET_SKILL_SETTINGS: TriggerNodeDTO(
            name=k.GET_SKILL_SETTINGS,
            trigger_key=k.GET_SKILL_SETTINGS,
            routes=TriggerRoutesDTO(default=k.SKILL_SETTINGS_RECEIVED),
        ),
        k.SKILL_SETTINGS_RECEIVED: TriggerNodeDTO(
            name=k.SKILL_SETTINGS_RECEIVED,
            trigger_key=k.SKILL_SETTINGS_RECEIVED,
            routes=TriggerRoutesDTO(yes=k.HAS_NUMERIC_IDENTIFIER, no=k.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        k.HAS_NUMERIC_IDENTIFIER: TriggerNodeDTO(
            name=k.HAS_NUMERIC_IDENTIFIER,
            trigger_key=k.HAS_NUMERIC_IDENTIFIER,
            routes=TriggerRoutesDTO(yes=k.SKILL_ACTIVE, no=k.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        k.SKILL_ACTIVE: TriggerNodeDTO(
            name=k.SKILL_ACTIVE,
            trigger_key=k.SKILL_ACTIVE,
            routes=TriggerRoutesDTO(yes=k.IS_TRANSFER_FORBIDDEN, no=k.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        k.IS_TRANSFER_FORBIDDEN: TriggerNodeDTO(
            name=k.IS_TRANSFER_FORBIDDEN,
            trigger_key=k.IS_TRANSFER_FORBIDDEN,
            routes=TriggerRoutesDTO(yes=k.WORKTIME_ENABLED, no=k.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        k.WORKTIME_ENABLED: TriggerNodeDTO(
            name=k.WORKTIME_ENABLED,
            trigger_key=k.WORKTIME_ENABLED,
            routes=TriggerRoutesDTO(yes=k.WORKTIME_RANGE_SINGLE_VALUE, no=k.APPEND_CURRENT_SKILL),
        ),
        k.WORKTIME_RANGE_SINGLE_VALUE: TriggerNodeDTO(
            name=k.WORKTIME_RANGE_SINGLE_VALUE,
            trigger_key=k.WORKTIME_RANGE_SINGLE_VALUE,
            routes=TriggerRoutesDTO(yes=k.APPEND_CURRENT_SKILL, no=k.IS_NOW_WORKTIME),
        ),
        k.IS_NOW_WORKTIME: TriggerNodeDTO(
            name=k.IS_NOW_WORKTIME,
            trigger_key=k.IS_NOW_WORKTIME,
            routes=TriggerRoutesDTO(yes=k.APPEND_CURRENT_SKILL, no=k.HAS_RESERVE_SKILL),
        ),
        k.HAS_RESERVE_SKILL: TriggerNodeDTO(
            name=k.HAS_RESERVE_SKILL,
            trigger_key=k.HAS_RESERVE_SKILL,
            routes=TriggerRoutesDTO(yes=k.APPEND_CURRENT_SKILL_FOR_RESERVE, no=k.STUB),
        ),
        k.APPEND_CURRENT_SKILL_FOR_RESERVE: TriggerNodeDTO(
            name=k.APPEND_CURRENT_SKILL_FOR_RESERVE,
            trigger_key=k.APPEND_CURRENT_SKILL_FOR_RESERVE,
            routes=TriggerRoutesDTO(default=k.RESERVE_SKILL_IN_SKILL_JSON_EXISTS),
        ),
        k.RESERVE_SKILL_IN_SKILL_JSON_EXISTS: TriggerNodeDTO(
            name=k.RESERVE_SKILL_IN_SKILL_JSON_EXISTS,
            trigger_key=k.RESERVE_SKILL_IN_SKILL_JSON_EXISTS,
            routes=TriggerRoutesDTO(yes=k.INCREMENT_WITH_RESERVE_TIMEOUT, no=k.FINISH_NO_RESERVE),
        ),
        k.INCREMENT_WITH_RESERVE_TIMEOUT: TriggerNodeDTO(
            name=k.INCREMENT_WITH_RESERVE_TIMEOUT,
            trigger_key=k.INCREMENT_WITH_RESERVE_TIMEOUT,
            routes=TriggerRoutesDTO(default=k.TAKE_RESERVE_SKILL_FROM_SMART_IVR),
        ),
        k.TAKE_RESERVE_SKILL_FROM_SMART_IVR: TriggerNodeDTO(
            name=k.TAKE_RESERVE_SKILL_FROM_SMART_IVR,
            trigger_key=k.TAKE_RESERVE_SKILL_FROM_SMART_IVR,
            routes=TriggerRoutesDTO(default=k.RESERVE_SKILL_FOUND),
        ),
        k.RESERVE_SKILL_FOUND: TriggerNodeDTO(
            name=k.RESERVE_SKILL_FOUND,
            trigger_key=k.RESERVE_SKILL_FOUND,
            routes=TriggerRoutesDTO(yes=k.SET_CURRENT_SKILL_TO_RESERVE, no=k.FINISH_NO_RESERVE),
        ),
        k.SET_CURRENT_SKILL_TO_RESERVE: TriggerNodeDTO(
            name=k.SET_CURRENT_SKILL_TO_RESERVE,
            trigger_key=k.SET_CURRENT_SKILL_TO_RESERVE,
            routes=TriggerRoutesDTO(default=k.APPEND_CURRENT_SKILL),
        ),
        k.STUB: TriggerNodeDTO(
            name=k.STUB,
            trigger_key=k.STUB,
            routes=TriggerRoutesDTO(default=k.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        k.CURRENT_SKILL_NUM_IS_ZERO: TriggerNodeDTO(
            name=k.CURRENT_SKILL_NUM_IS_ZERO,
            trigger_key=k.CURRENT_SKILL_NUM_IS_ZERO,
            routes=TriggerRoutesDTO(yes=k.APPEND_CURRENT_SKILL, no=k.FINISH_NO_RESERVE),
        ),
        k.APPEND_CURRENT_SKILL: TriggerNodeDTO(
            name=k.APPEND_CURRENT_SKILL,
            trigger_key=k.APPEND_CURRENT_SKILL,
            routes=TriggerRoutesDTO(default=k.FINISH),
        ),
        k.FINISH: TriggerNodeDTO(
            name=k.FINISH,
            trigger_key=k.FINISH,
            routes=TriggerRoutesDTO(),
        ),
        k.FINISH_NO_RESERVE: TriggerNodeDTO(
            name=k.FINISH_NO_RESERVE,
            trigger_key=k.FINISH,
            routes=TriggerRoutesDTO(),
        ),
    }

    if route_overrides:
        for node_name, routes in route_overrides.items():
            if node_name not in nodes:
                raise KeyError(f"Unknown node for route override: '{node_name}'")
            nodes[node_name].routes = routes

    return WorkflowDTO(start_node=k.INIT_SKILL_RUN, nodes=nodes)


def build_skill_routing_trigger_factories() -> dict[str, TriggerFactory]:
    k = SkillRoutingKey
    return {
        k.INIT_SKILL_RUN: lambda _: DefaultActionTrigger(_init_skill_run),
        k.IS_TRANSFER: lambda _: PredicateTrigger(lambda c: c.is_transfer),
        k.CLASSIFICATION_SKILL_ID_IS_NULL: lambda _: PredicateTrigger(
            lambda c: c.classification_skill_id is None
        ),
        k.RESOLVE_SKILL_FROM_ROUTE_DEFAULT: lambda _: DefaultActionTrigger(_set_route_default_skill),
        k.IS_TWORK_DATA_SKILL_ID_NULL: lambda _: PredicateTrigger(lambda c: c.twork_data_skill_id is None),
        k.RESOLVE_RETRANSFER_SKILL: lambda _: DefaultActionTrigger(_set_retransfer_skill),
        k.APPEND_RETRANSFER_SKILL: lambda _: DefaultActionTrigger(_append_retransfer_skill),
        k.IS_TRANSFER_AFTER_TWORK: lambda _: PredicateTrigger(lambda c: c.is_transfer),
        k.RESOLVE_TRANSFER_SKILL: lambda _: DefaultActionTrigger(_set_transfer_skill),
        k.APPEND_TRANSFER_SKILL: lambda _: DefaultActionTrigger(_append_transfer_skill),
        k.GET_SKILL_SETTINGS: lambda _: DefaultActionTrigger(_fallback_to_classification_skill),
        k.SKILL_SETTINGS_RECEIVED: lambda _: PredicateTrigger(lambda c: c.skill_settings_received),
        k.HAS_NUMERIC_IDENTIFIER: lambda _: PredicateTrigger(lambda c: c.numeric_identifier_present),
        k.SKILL_ACTIVE: lambda _: PredicateTrigger(lambda c: c.skill_active),
        k.IS_TRANSFER_FORBIDDEN: lambda _: PredicateTrigger(lambda c: not c.transfer_allowed),
        k.WORKTIME_ENABLED: lambda _: PredicateTrigger(lambda c: c.worktime_enabled),
        k.WORKTIME_RANGE_SINGLE_VALUE: lambda _: PredicateTrigger(lambda c: c.worktime_range_single_value),
        k.IS_NOW_WORKTIME: lambda _: PredicateTrigger(lambda c: c.is_now_worktime),
        k.HAS_RESERVE_SKILL: lambda _: PredicateTrigger(lambda c: c.has_reserve_skill),
        k.APPEND_CURRENT_SKILL_FOR_RESERVE: lambda _: DefaultActionTrigger(_append_current_skill),
        k.RESERVE_SKILL_IN_SKILL_JSON_EXISTS: lambda _: PredicateTrigger(
            lambda c: c.reserve_skill_exists_in_skill_json
        ),
        k.INCREMENT_WITH_RESERVE_TIMEOUT: lambda _: DefaultActionTrigger(_increment_with_reserve_timeout),
        k.TAKE_RESERVE_SKILL_FROM_SMART_IVR: lambda _: DefaultActionTrigger(_set_skill_from_smart_ivr),
        k.RESERVE_SKILL_FOUND: lambda _: PredicateTrigger(lambda c: c.reserve_skill_found),
        k.SET_CURRENT_SKILL_TO_RESERVE: lambda _: DefaultActionTrigger(_set_skill_from_smart_ivr),
        k.STUB: lambda _: DefaultActionTrigger(),
        k.CURRENT_SKILL_NUM_IS_ZERO: lambda _: PredicateTrigger(lambda c: c.skill_num == 0),
        k.APPEND_CURRENT_SKILL: lambda _: DefaultActionTrigger(_append_current_skill),
        k.FINISH: lambda _: DefaultActionTrigger(),
    }


def build_skill_routing_state_machine(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> StatefulWorkflow:
    workflow = build_skill_routing_workflow(route_overrides=route_overrides)
    return StatefulWorkflow(
        workflow=workflow,
        trigger_factories=build_skill_routing_trigger_factories(),
    )
