import unittest

from state_machine.dto import (
    TriggerContextDTO,
    TriggerNodeDTO,
    TriggerRoutesDTO,
    WorkflowDTO,
)
from state_machine.engine import StatefulWorkflow
from state_machine.triggers import AlwaysNoTrigger, AlwaysYesTrigger, ContainsKeyTrigger


class StateMachineTests(unittest.TestCase):
    def test_yes_no_and_default_routing(self) -> None:
        workflow = WorkflowDTO(
            start_node="check",
            nodes={
                "check": TriggerNodeDTO(
                    name="check",
                    trigger_key="contains_key",
                    options={"required_key": "approved"},
                    routes=TriggerRoutesDTO(yes="approved", default="rejected"),
                ),
                "approved": TriggerNodeDTO(
                    name="approved",
                    trigger_key="always_yes",
                    routes=TriggerRoutesDTO(),
                ),
                "rejected": TriggerNodeDTO(
                    name="rejected",
                    trigger_key="always_no",
                    routes=TriggerRoutesDTO(),
                ),
            },
        )
        workflow_machine = StatefulWorkflow(
            workflow=workflow,
            trigger_factories={
                "contains_key": lambda options: ContainsKeyTrigger(
                    required_key=options["required_key"]
                ),
                "always_yes": lambda _: AlwaysYesTrigger(),
                "always_no": lambda _: AlwaysNoTrigger(),
            },
        )

        yes_history = workflow_machine.run(
            TriggerContextDTO(payload={"approved": True}),
        )
        self.assertEqual([item.node for item in yes_history], ["check", "approved"])
        self.assertEqual(yes_history[0].next_node, "approved")
        self.assertEqual(workflow_machine.current_node, "approved")

    def test_default_route_when_key_is_absent(self) -> None:
        workflow = WorkflowDTO(
            start_node="check",
            nodes={
                "check": TriggerNodeDTO(
                    name="check",
                    trigger_key="contains_key",
                    options={"required_key": "approved"},
                    routes=TriggerRoutesDTO(yes="approved", default="rejected"),
                ),
                "approved": TriggerNodeDTO(
                    name="approved",
                    trigger_key="always_yes",
                    routes=TriggerRoutesDTO(),
                ),
                "rejected": TriggerNodeDTO(
                    name="rejected",
                    trigger_key="always_no",
                    routes=TriggerRoutesDTO(),
                ),
            },
        )
        workflow_machine = StatefulWorkflow(
            workflow=workflow,
            trigger_factories={
                "contains_key": lambda options: ContainsKeyTrigger(
                    required_key=options["required_key"]
                ),
                "always_yes": lambda _: AlwaysYesTrigger(),
                "always_no": lambda _: AlwaysNoTrigger(),
            },
        )

        history = workflow_machine.run(TriggerContextDTO(payload={}))
        self.assertEqual([item.node for item in history], ["check", "rejected"])
        self.assertEqual(history[0].next_node, "rejected")
        self.assertEqual(workflow_machine.current_node, "rejected")

    def test_dynamic_node_graph(self) -> None:
        workflow = WorkflowDTO(
            start_node="first",
            nodes={
                "first": TriggerNodeDTO(
                    name="first",
                    trigger_key="always_yes",
                    routes=TriggerRoutesDTO(yes="second"),
                ),
                "second": TriggerNodeDTO(
                    name="second",
                    trigger_key="always_no",
                    routes=TriggerRoutesDTO(no="third"),
                ),
                "third": TriggerNodeDTO(
                    name="third",
                    trigger_key="always_yes",
                    routes=TriggerRoutesDTO(),
                ),
            },
        )
        workflow_machine = StatefulWorkflow(
            workflow=workflow,
            trigger_factories={
                "always_yes": lambda _: AlwaysYesTrigger(),
                "always_no": lambda _: AlwaysNoTrigger(),
            },
        )

        history = workflow_machine.run(TriggerContextDTO())
        self.assertEqual([item.node for item in history], ["first", "second", "third"])
        self.assertEqual(workflow_machine.current_node, "third")


if __name__ == "__main__":
    unittest.main()
