import unittest

from state_machine.skill_routing import (
    IsTransferTrigger,
    MachineState,
    SkillRoutingContextDTO,
    SkillRoutingKeys,
    SkillRoutingStateMachineFactory,
    build_skill_routing_workflow,
    build_skill_routing_state_machine,
)
from state_machine.dto import TriggerRoutesDTO


class SkillRoutingSchemeTests(unittest.TestCase):
    def test_factory_create_builds_machine(self) -> None:
        machine = SkillRoutingStateMachineFactory().create()
        self.assertIsInstance(machine, MachineState)
        self.assertEqual(machine.current_node, SkillRoutingKeys.INIT_SKILL_RUN)

    def test_factory_trigger_factories_resolve_from_di(self) -> None:
        trigger_factories = SkillRoutingStateMachineFactory().create_trigger_factories()
        first = trigger_factories[SkillRoutingKeys.IS_TRANSFER]()
        second = trigger_factories[SkillRoutingKeys.IS_TRANSFER]()
        self.assertIsInstance(first, IsTransferTrigger)
        self.assertIsInstance(second, IsTransferTrigger)
        self.assertIsNot(first, second)

    def test_skill_routing_workflow_has_no_cycles(self) -> None:
        workflow = build_skill_routing_workflow()
        self.assertEqual(workflow.start_node, SkillRoutingKeys.INIT_SKILL_RUN)
        self.assertEqual(
            workflow.nodes[SkillRoutingKeys.IS_TRANSFER].trigger_name,
            IsTransferTrigger.name,
        )
        self.assertEqual(
            workflow.nodes[SkillRoutingKeys.IS_TRANSFER].trigger_doc,
            IsTransferTrigger.doc,
        )

    def test_cycle_in_route_override_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Detected cycle in skill routing workflow"):
            build_skill_routing_workflow(
                route_overrides={
                    SkillRoutingKeys.APPEND_CURRENT_SKILL: TriggerRoutesDTO(
                        default=SkillRoutingKeys.GET_SKILL_SETTINGS
                    )
                }
            )

    def test_transfer_path_with_route_default_skill(self) -> None:
        machine = build_skill_routing_state_machine()
        context = SkillRoutingContextDTO(
            is_transfer=True,
            classification_skill_id=None,
            route_default_skill_mapping="route-default-skill",
            skill_settings_received=True,
            numeric_identifier_present=True,
            skill_active=True,
            transfer_allowed=False,
            worktime_enabled=True,
            worktime_range_single_value=True,
        )

        history = machine.run(context)

        self.assertEqual(history[-1].node, "finish")
        self.assertEqual(context.skill_json[-1]["id"], "route-default-skill")
        self.assertEqual(context.skill_json[-1]["wait_time"], 0)

    def test_retransfer_fallback_path(self) -> None:
        machine = build_skill_routing_state_machine()
        context = SkillRoutingContextDTO(
            is_transfer=False,
            twork_data_skill_id=None,
            retransfer_default_skill_id="retransfer-default-skill",
        )

        history = machine.run(context)

        self.assertEqual([step.node for step in history][-2:], ["append_retransfer_skill", "finish"])
        self.assertEqual(
            context.skill_json,
            [
                {
                    "id": "retransfer-default-skill",
                    "key": "call_ui3_RETRANSFER_DEFAULT_SKILL_ID",
                    "wait_time": 0,
                }
            ],
        )

    def test_reserve_branch_sets_timeout_and_appends_reserve_skill(self) -> None:
        machine = build_skill_routing_state_machine()
        context = SkillRoutingContextDTO(
            is_transfer=True,
            classification_skill_id="main-skill",
            skill_settings_received=True,
            numeric_identifier_present=True,
            skill_active=True,
            transfer_allowed=False,
            worktime_enabled=True,
            worktime_range_single_value=False,
            is_now_worktime=False,
            has_reserve_skill=True,
            reserve_skill_exists_in_skill_json=True,
            reserve_skill_timeout=25,
            reserve_skill_found=True,
            smart_ivr_id_skill="reserve-skill",
        )

        history = machine.run(context)

        self.assertEqual(history[-1].node, "finish")
        self.assertEqual(context.skill_num, 1)
        self.assertEqual(context.wait_time, 25)
        self.assertEqual(context.skill_json[-1]["id"], "reserve-skill")
        self.assertEqual(context.skill_json[-1]["wait_time"], 25)


if __name__ == "__main__":
    unittest.main()
