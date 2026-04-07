import unittest

from state_machine.skill_routing import (
    SkillRoutingContextDTO,
    build_skill_routing_state_machine,
)


class SkillRoutingSchemeTests(unittest.TestCase):
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
