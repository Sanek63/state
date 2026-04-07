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


class AppendCurrentSkillForReserveTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        context.skill_json.append(
            {
                "id": context.skill_id,
                "key": context.skill_id,
                "wait_time": context.wait_time,
            }
        )
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


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


class SetCurrentSkillToReserveTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        if context.smart_ivr_id_skill:
            context.skill_id = context.smart_ivr_id_skill
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class StubTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


class FinishTrigger(BaseTrigger):
    def execute(self, context: SkillRoutingContextDTO) -> TriggerExecutionDTO:
        return TriggerExecutionDTO(decision=DecisionDTO.DEFAULT)


def build_skill_routing_workflow(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> WorkflowDTO:
    nodes: dict[str, TriggerNodeDTO] = {
        "init_skill_run": TriggerNodeDTO(
            name="init_skill_run",
            trigger_key="init_skill_run",
            routes=TriggerRoutesDTO(default="is_transfer"),
        ),
        "is_transfer": TriggerNodeDTO(
            name="is_transfer",
            trigger_key="is_transfer",
            routes=TriggerRoutesDTO(yes="classification_skill_id_is_null", no="is_twork_data_skill_id_null"),
        ),
        "classification_skill_id_is_null": TriggerNodeDTO(
            name="classification_skill_id_is_null",
            trigger_key="classification_skill_id_is_null",
            routes=TriggerRoutesDTO(yes="resolve_skill_from_route_default", no="get_skill_settings"),
        ),
        "resolve_skill_from_route_default": TriggerNodeDTO(
            name="resolve_skill_from_route_default",
            trigger_key="resolve_skill_from_route_default",
            routes=TriggerRoutesDTO(default="get_skill_settings"),
        ),
        "is_twork_data_skill_id_null": TriggerNodeDTO(
            name="is_twork_data_skill_id_null",
            trigger_key="is_twork_data_skill_id_null",
            routes=TriggerRoutesDTO(yes="resolve_retransfer_skill", no="is_transfer_after_twork"),
        ),
        "resolve_retransfer_skill": TriggerNodeDTO(
            name="resolve_retransfer_skill",
            trigger_key="resolve_retransfer_skill",
            routes=TriggerRoutesDTO(default="append_retransfer_skill"),
        ),
        "append_retransfer_skill": TriggerNodeDTO(
            name="append_retransfer_skill",
            trigger_key="append_retransfer_skill",
            routes=TriggerRoutesDTO(default="finish"),
        ),
        "is_transfer_after_twork": TriggerNodeDTO(
            name="is_transfer_after_twork",
            trigger_key="is_transfer_after_twork",
            routes=TriggerRoutesDTO(yes="resolve_transfer_skill", no="get_skill_settings"),
        ),
        "resolve_transfer_skill": TriggerNodeDTO(
            name="resolve_transfer_skill",
            trigger_key="resolve_transfer_skill",
            routes=TriggerRoutesDTO(default="append_transfer_skill"),
        ),
        "append_transfer_skill": TriggerNodeDTO(
            name="append_transfer_skill",
            trigger_key="append_transfer_skill",
            routes=TriggerRoutesDTO(default="finish"),
        ),
        "get_skill_settings": TriggerNodeDTO(
            name="get_skill_settings",
            trigger_key="get_skill_settings",
            routes=TriggerRoutesDTO(default="skill_settings_received"),
        ),
        "skill_settings_received": TriggerNodeDTO(
            name="skill_settings_received",
            trigger_key="skill_settings_received",
            routes=TriggerRoutesDTO(yes="has_numeric_identifier", no="current_skill_num_is_zero"),
        ),
        "has_numeric_identifier": TriggerNodeDTO(
            name="has_numeric_identifier",
            trigger_key="has_numeric_identifier",
            routes=TriggerRoutesDTO(yes="skill_active", no="current_skill_num_is_zero"),
        ),
        "skill_active": TriggerNodeDTO(
            name="skill_active",
            trigger_key="skill_active",
            routes=TriggerRoutesDTO(yes="is_transfer_forbidden", no="current_skill_num_is_zero"),
        ),
        "is_transfer_forbidden": TriggerNodeDTO(
            name="is_transfer_forbidden",
            trigger_key="is_transfer_forbidden",
            routes=TriggerRoutesDTO(yes="worktime_enabled", no="current_skill_num_is_zero"),
        ),
        "worktime_enabled": TriggerNodeDTO(
            name="worktime_enabled",
            trigger_key="worktime_enabled",
            routes=TriggerRoutesDTO(yes="worktime_range_single_value", no="append_current_skill"),
        ),
        "worktime_range_single_value": TriggerNodeDTO(
            name="worktime_range_single_value",
            trigger_key="worktime_range_single_value",
            routes=TriggerRoutesDTO(yes="append_current_skill", no="is_now_worktime"),
        ),
        "is_now_worktime": TriggerNodeDTO(
            name="is_now_worktime",
            trigger_key="is_now_worktime",
            routes=TriggerRoutesDTO(yes="append_current_skill", no="has_reserve_skill"),
        ),
        "has_reserve_skill": TriggerNodeDTO(
            name="has_reserve_skill",
            trigger_key="has_reserve_skill",
            routes=TriggerRoutesDTO(yes="append_current_skill_for_reserve", no="stub"),
        ),
        "append_current_skill_for_reserve": TriggerNodeDTO(
            name="append_current_skill_for_reserve",
            trigger_key="append_current_skill_for_reserve",
            routes=TriggerRoutesDTO(default="reserve_skill_in_skill_json_exists"),
        ),
        "reserve_skill_in_skill_json_exists": TriggerNodeDTO(
            name="reserve_skill_in_skill_json_exists",
            trigger_key="reserve_skill_in_skill_json_exists",
            routes=TriggerRoutesDTO(yes="increment_with_reserve_timeout", no="finish_no_reserve"),
        ),
        "increment_with_reserve_timeout": TriggerNodeDTO(
            name="increment_with_reserve_timeout",
            trigger_key="increment_with_reserve_timeout",
            routes=TriggerRoutesDTO(default="take_reserve_skill_from_smart_ivr"),
        ),
        "take_reserve_skill_from_smart_ivr": TriggerNodeDTO(
            name="take_reserve_skill_from_smart_ivr",
            trigger_key="take_reserve_skill_from_smart_ivr",
            routes=TriggerRoutesDTO(default="reserve_skill_found"),
        ),
        "reserve_skill_found": TriggerNodeDTO(
            name="reserve_skill_found",
            trigger_key="reserve_skill_found",
            routes=TriggerRoutesDTO(yes="set_current_skill_to_reserve", no="finish_no_reserve"),
        ),
        "set_current_skill_to_reserve": TriggerNodeDTO(
            name="set_current_skill_to_reserve",
            trigger_key="set_current_skill_to_reserve",
            routes=TriggerRoutesDTO(default="append_current_skill"),
        ),
        "stub": TriggerNodeDTO(
            name="stub",
            trigger_key="stub",
            routes=TriggerRoutesDTO(default="current_skill_num_is_zero"),
        ),
        "current_skill_num_is_zero": TriggerNodeDTO(
            name="current_skill_num_is_zero",
            trigger_key="current_skill_num_is_zero",
            routes=TriggerRoutesDTO(yes="append_current_skill", no="finish_no_reserve"),
        ),
        "append_current_skill": TriggerNodeDTO(
            name="append_current_skill",
            trigger_key="append_current_skill",
            routes=TriggerRoutesDTO(default="finish"),
        ),
        "finish": TriggerNodeDTO(
            name="finish",
            trigger_key="finish",
            routes=TriggerRoutesDTO(),
        ),
        "finish_no_reserve": TriggerNodeDTO(
            name="finish_no_reserve",
            trigger_key="finish",
            routes=TriggerRoutesDTO(),
        ),
    }

    if route_overrides:
        for node_name, routes in route_overrides.items():
            if node_name not in nodes:
                raise KeyError(f"Unknown node for route override: '{node_name}'")
            nodes[node_name].routes = routes

    return WorkflowDTO(start_node="init_skill_run", nodes=nodes)


def build_skill_routing_trigger_factories() -> dict[str, TriggerFactory]:
    return {
        "init_skill_run": lambda _: InitSkillRunTrigger(),
        "is_transfer": lambda _: IsTransferTrigger(),
        "classification_skill_id_is_null": lambda _: IsClassificationSkillIdNullTrigger(),
        "resolve_skill_from_route_default": lambda _: ResolveSkillFromRouteDefaultTrigger(),
        "is_twork_data_skill_id_null": lambda _: IsTworkDataSkillIdNullTrigger(),
        "resolve_retransfer_skill": lambda _: ResolveRetransferSkillTrigger(),
        "append_retransfer_skill": lambda _: AppendRetransferSkillTrigger(),
        "is_transfer_after_twork": lambda _: IsTransferAfterTworkTrigger(),
        "resolve_transfer_skill": lambda _: ResolveTransferSkillTrigger(),
        "append_transfer_skill": lambda _: AppendTransferSkillTrigger(),
        "get_skill_settings": lambda _: GetSkillSettingsTrigger(),
        "skill_settings_received": lambda _: SkillSettingsReceivedTrigger(),
        "has_numeric_identifier": lambda _: HasNumericIdentifierTrigger(),
        "skill_active": lambda _: IsSkillActiveTrigger(),
        "is_transfer_forbidden": lambda _: IsTransferForbiddenTrigger(),
        "worktime_enabled": lambda _: IsWorktimeEnabledTrigger(),
        "worktime_range_single_value": lambda _: IsWorktimeRangeSingleValueTrigger(),
        "is_now_worktime": lambda _: IsNowWorktimeTrigger(),
        "has_reserve_skill": lambda _: HasReserveSkillTrigger(),
        "append_current_skill_for_reserve": lambda _: AppendCurrentSkillForReserveTrigger(),
        "reserve_skill_in_skill_json_exists": lambda _: ReserveSkillInSkillJsonExistsTrigger(),
        "increment_with_reserve_timeout": lambda _: IncrementWithReserveTimeoutTrigger(),
        "take_reserve_skill_from_smart_ivr": lambda _: TakeReserveSkillFromSmartIvrTrigger(),
        "reserve_skill_found": lambda _: ReserveSkillFoundTrigger(),
        "set_current_skill_to_reserve": lambda _: SetCurrentSkillToReserveTrigger(),
        "stub": lambda _: StubTrigger(),
        "current_skill_num_is_zero": lambda _: CurrentSkillNumIsZeroTrigger(),
        "append_current_skill": lambda _: AppendCurrentSkillTrigger(),
        "finish": lambda _: FinishTrigger(),
    }


def build_skill_routing_state_machine(
    route_overrides: dict[str, TriggerRoutesDTO] | None = None,
) -> StatefulWorkflow:
    workflow = build_skill_routing_workflow(route_overrides=route_overrides)
    return StatefulWorkflow(
        workflow=workflow,
        trigger_factories=build_skill_routing_trigger_factories(),
    )
