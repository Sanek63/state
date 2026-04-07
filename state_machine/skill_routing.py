from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

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
def build_skill_routing_workflow(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> WorkflowDTO:
    n = SkillRoutingKeys
    t = SkillRoutingKeys
    nodes: dict[str, TriggerNodeDTO] = {
        n.INIT_SKILL_RUN: TriggerNodeDTO(
            name=n.INIT_SKILL_RUN,
            trigger_key=t.INIT_SKILL_RUN,
            routes=TriggerRoutesDTO(default=n.IS_TRANSFER),
        ),
        n.IS_TRANSFER: TriggerNodeDTO(
            name=n.IS_TRANSFER,
            trigger_key=t.IS_TRANSFER,
            routes=TriggerRoutesDTO(
                yes=n.CLASSIFICATION_SKILL_ID_IS_NULL,
                no=n.IS_TWORK_DATA_SKILL_ID_NULL,
            ),
        ),
        n.CLASSIFICATION_SKILL_ID_IS_NULL: TriggerNodeDTO(
            name=n.CLASSIFICATION_SKILL_ID_IS_NULL,
            trigger_key=t.CLASSIFICATION_SKILL_ID_IS_NULL,
            routes=TriggerRoutesDTO(
                yes=n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
                no=n.GET_SKILL_SETTINGS,
            ),
        ),
        n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT: TriggerNodeDTO(
            name=n.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
            trigger_key=t.RESOLVE_SKILL_FROM_ROUTE_DEFAULT,
            routes=TriggerRoutesDTO(default=n.GET_SKILL_SETTINGS),
        ),
        n.IS_TWORK_DATA_SKILL_ID_NULL: TriggerNodeDTO(
            name=n.IS_TWORK_DATA_SKILL_ID_NULL,
            trigger_key=t.IS_TWORK_DATA_SKILL_ID_NULL,
            routes=TriggerRoutesDTO(
                yes=n.RESOLVE_RETRANSFER_SKILL,
                no=n.IS_TRANSFER_AFTER_TWORK,
            ),
        ),
        n.RESOLVE_RETRANSFER_SKILL: TriggerNodeDTO(
            name=n.RESOLVE_RETRANSFER_SKILL,
            trigger_key=t.RESOLVE_RETRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=n.APPEND_RETRANSFER_SKILL),
        ),
        n.APPEND_RETRANSFER_SKILL: TriggerNodeDTO(
            name=n.APPEND_RETRANSFER_SKILL,
            trigger_key=t.APPEND_RETRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.IS_TRANSFER_AFTER_TWORK: TriggerNodeDTO(
            name=n.IS_TRANSFER_AFTER_TWORK,
            trigger_key=t.IS_TRANSFER_AFTER_TWORK,
            routes=TriggerRoutesDTO(yes=n.RESOLVE_TRANSFER_SKILL, no=n.GET_SKILL_SETTINGS),
        ),
        n.RESOLVE_TRANSFER_SKILL: TriggerNodeDTO(
            name=n.RESOLVE_TRANSFER_SKILL,
            trigger_key=t.RESOLVE_TRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=n.APPEND_TRANSFER_SKILL),
        ),
        n.APPEND_TRANSFER_SKILL: TriggerNodeDTO(
            name=n.APPEND_TRANSFER_SKILL,
            trigger_key=t.APPEND_TRANSFER_SKILL,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.GET_SKILL_SETTINGS: TriggerNodeDTO(
            name=n.GET_SKILL_SETTINGS,
            trigger_key=t.GET_SKILL_SETTINGS,
            routes=TriggerRoutesDTO(default=n.SKILL_SETTINGS_RECEIVED),
        ),
        n.SKILL_SETTINGS_RECEIVED: TriggerNodeDTO(
            name=n.SKILL_SETTINGS_RECEIVED,
            trigger_key=t.SKILL_SETTINGS_RECEIVED,
            routes=TriggerRoutesDTO(yes=n.HAS_NUMERIC_IDENTIFIER, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.HAS_NUMERIC_IDENTIFIER: TriggerNodeDTO(
            name=n.HAS_NUMERIC_IDENTIFIER,
            trigger_key=t.HAS_NUMERIC_IDENTIFIER,
            routes=TriggerRoutesDTO(yes=n.SKILL_ACTIVE, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.SKILL_ACTIVE: TriggerNodeDTO(
            name=n.SKILL_ACTIVE,
            trigger_key=t.SKILL_ACTIVE,
            routes=TriggerRoutesDTO(yes=n.IS_TRANSFER_FORBIDDEN, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.IS_TRANSFER_FORBIDDEN: TriggerNodeDTO(
            name=n.IS_TRANSFER_FORBIDDEN,
            trigger_key=t.IS_TRANSFER_FORBIDDEN,
            routes=TriggerRoutesDTO(yes=n.WORKTIME_ENABLED, no=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.WORKTIME_ENABLED: TriggerNodeDTO(
            name=n.WORKTIME_ENABLED,
            trigger_key=t.WORKTIME_ENABLED,
            routes=TriggerRoutesDTO(yes=n.WORKTIME_RANGE_SINGLE_VALUE, no=n.APPEND_CURRENT_SKILL),
        ),
        n.WORKTIME_RANGE_SINGLE_VALUE: TriggerNodeDTO(
            name=n.WORKTIME_RANGE_SINGLE_VALUE,
            trigger_key=t.WORKTIME_RANGE_SINGLE_VALUE,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.IS_NOW_WORKTIME),
        ),
        n.IS_NOW_WORKTIME: TriggerNodeDTO(
            name=n.IS_NOW_WORKTIME,
            trigger_key=t.IS_NOW_WORKTIME,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.HAS_RESERVE_SKILL),
        ),
        n.HAS_RESERVE_SKILL: TriggerNodeDTO(
            name=n.HAS_RESERVE_SKILL,
            trigger_key=t.HAS_RESERVE_SKILL,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL_FOR_RESERVE, no=n.STUB),
        ),
        n.APPEND_CURRENT_SKILL_FOR_RESERVE: TriggerNodeDTO(
            name=n.APPEND_CURRENT_SKILL_FOR_RESERVE,
            trigger_key=t.APPEND_CURRENT_SKILL_FOR_RESERVE,
            routes=TriggerRoutesDTO(default=n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS),
        ),
        n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS: TriggerNodeDTO(
            name=n.RESERVE_SKILL_IN_SKILL_JSON_EXISTS,
            trigger_key=t.RESERVE_SKILL_IN_SKILL_JSON_EXISTS,
            routes=TriggerRoutesDTO(yes=n.INCREMENT_WITH_RESERVE_TIMEOUT, no=n.FINISH_NO_RESERVE),
        ),
        n.INCREMENT_WITH_RESERVE_TIMEOUT: TriggerNodeDTO(
            name=n.INCREMENT_WITH_RESERVE_TIMEOUT,
            trigger_key=t.INCREMENT_WITH_RESERVE_TIMEOUT,
            routes=TriggerRoutesDTO(default=n.TAKE_RESERVE_SKILL_FROM_SMART_IVR),
        ),
        n.TAKE_RESERVE_SKILL_FROM_SMART_IVR: TriggerNodeDTO(
            name=n.TAKE_RESERVE_SKILL_FROM_SMART_IVR,
            trigger_key=t.TAKE_RESERVE_SKILL_FROM_SMART_IVR,
            routes=TriggerRoutesDTO(default=n.RESERVE_SKILL_FOUND),
        ),
        n.RESERVE_SKILL_FOUND: TriggerNodeDTO(
            name=n.RESERVE_SKILL_FOUND,
            trigger_key=t.RESERVE_SKILL_FOUND,
            routes=TriggerRoutesDTO(yes=n.SET_CURRENT_SKILL_TO_RESERVE, no=n.FINISH_NO_RESERVE),
        ),
        n.SET_CURRENT_SKILL_TO_RESERVE: TriggerNodeDTO(
            name=n.SET_CURRENT_SKILL_TO_RESERVE,
            trigger_key=t.SET_CURRENT_SKILL_TO_RESERVE,
            routes=TriggerRoutesDTO(default=n.APPEND_CURRENT_SKILL),
        ),
        n.STUB: TriggerNodeDTO(
            name=n.STUB,
            trigger_key=t.STUB,
            routes=TriggerRoutesDTO(default=n.CURRENT_SKILL_NUM_IS_ZERO),
        ),
        n.CURRENT_SKILL_NUM_IS_ZERO: TriggerNodeDTO(
            name=n.CURRENT_SKILL_NUM_IS_ZERO,
            trigger_key=t.CURRENT_SKILL_NUM_IS_ZERO,
            routes=TriggerRoutesDTO(yes=n.APPEND_CURRENT_SKILL, no=n.FINISH_NO_RESERVE),
        ),
        n.APPEND_CURRENT_SKILL: TriggerNodeDTO(
            name=n.APPEND_CURRENT_SKILL,
            trigger_key=t.APPEND_CURRENT_SKILL,
            routes=TriggerRoutesDTO(default=n.FINISH),
        ),
        n.FINISH: TriggerNodeDTO(
            name=n.FINISH,
            trigger_key=t.FINISH,
            routes=TriggerRoutesDTO(),
        ),
        n.FINISH_NO_RESERVE: TriggerNodeDTO(
            name=n.FINISH_NO_RESERVE,
            trigger_key=t.FINISH,
            routes=TriggerRoutesDTO(),
        ),
    }

    if route_overrides:
        for node_name, routes in route_overrides.items():
            if node_name not in nodes:
                raise KeyError(f"Unknown node for route override: '{node_name}'")
            nodes[node_name].routes = routes

    return WorkflowDTO(start_node=n.INIT_SKILL_RUN, nodes=nodes)


def build_skill_routing_trigger_factories() -> dict[str, TriggerFactory]:
    t = SkillRoutingKeys
    return {
        t.INIT_SKILL_RUN: lambda: InitSkillRunTrigger(),
        t.IS_TRANSFER: lambda: IsTransferTrigger(),
        t.CLASSIFICATION_SKILL_ID_IS_NULL: lambda: IsClassificationSkillIdNullTrigger(),
        t.RESOLVE_SKILL_FROM_ROUTE_DEFAULT: lambda: ResolveSkillFromRouteDefaultTrigger(),
        t.IS_TWORK_DATA_SKILL_ID_NULL: lambda: IsTworkDataSkillIdNullTrigger(),
        t.RESOLVE_RETRANSFER_SKILL: lambda: ResolveRetransferSkillTrigger(),
        t.APPEND_RETRANSFER_SKILL: lambda: AppendRetransferSkillTrigger(),
        t.IS_TRANSFER_AFTER_TWORK: lambda: IsTransferAfterTworkTrigger(),
        t.RESOLVE_TRANSFER_SKILL: lambda: ResolveTransferSkillTrigger(),
        t.APPEND_TRANSFER_SKILL: lambda: AppendTransferSkillTrigger(),
        t.GET_SKILL_SETTINGS: lambda: GetSkillSettingsTrigger(),
        t.SKILL_SETTINGS_RECEIVED: lambda: SkillSettingsReceivedTrigger(),
        t.HAS_NUMERIC_IDENTIFIER: lambda: HasNumericIdentifierTrigger(),
        t.SKILL_ACTIVE: lambda: IsSkillActiveTrigger(),
        t.IS_TRANSFER_FORBIDDEN: lambda: IsTransferForbiddenTrigger(),
        t.WORKTIME_ENABLED: lambda: IsWorktimeEnabledTrigger(),
        t.WORKTIME_RANGE_SINGLE_VALUE: lambda: IsWorktimeRangeSingleValueTrigger(),
        t.IS_NOW_WORKTIME: lambda: IsNowWorktimeTrigger(),
        t.HAS_RESERVE_SKILL: lambda: HasReserveSkillTrigger(),
        t.APPEND_CURRENT_SKILL_FOR_RESERVE: lambda: AppendCurrentSkillForReserveTrigger(),
        t.RESERVE_SKILL_IN_SKILL_JSON_EXISTS: lambda: ReserveSkillInSkillJsonExistsTrigger(),
        t.INCREMENT_WITH_RESERVE_TIMEOUT: lambda: IncrementWithReserveTimeoutTrigger(),
        t.TAKE_RESERVE_SKILL_FROM_SMART_IVR: lambda: TakeReserveSkillFromSmartIvrTrigger(),
        t.RESERVE_SKILL_FOUND: lambda: ReserveSkillFoundTrigger(),
        t.SET_CURRENT_SKILL_TO_RESERVE: lambda: SetCurrentSkillToReserveTrigger(),
        t.STUB: lambda: StubTrigger(),
        t.CURRENT_SKILL_NUM_IS_ZERO: lambda: CurrentSkillNumIsZeroTrigger(),
        t.APPEND_CURRENT_SKILL: lambda: AppendCurrentSkillTrigger(),
        t.FINISH: lambda: FinishTrigger(),
    }


def build_skill_routing_state_machine(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> StatefulWorkflow:
    workflow = build_skill_routing_workflow(route_overrides=route_overrides)
    return StatefulWorkflow(
        workflow=workflow,
        trigger_factories=build_skill_routing_trigger_factories(),
    )
