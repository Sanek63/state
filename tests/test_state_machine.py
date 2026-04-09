import unittest
from dataclasses import dataclass

from state_machine.dto import (
    TriggerContextDTO,
    TriggerNodeDTO,
    TriggerRoutesDTO,
    WorkflowDTO,
)
from state_machine.engine import StatefulWorkflow
from state_machine.triggers import AlwaysNoTrigger, AlwaysYesTrigger, ContainsKeyTrigger


class StateMachineTests(unittest.TestCase):
    @dataclass(slots=True)
    class _ApprovedContext(TriggerContextDTO):
        approved: bool | None = None

    def test_can_build_workflow_graph(self) -> None:
        workflow = WorkflowDTO(
            start_node="first",
            nodes={
                "first": TriggerNodeDTO(
                    name="first",
                    trigger_key="always_yes",
                    trigger_name="Always YES",
                    trigger_doc="Always returns YES decision.",
                    routes=TriggerRoutesDTO(yes="second"),
                ),
                "second": TriggerNodeDTO(
                    name="second",
                    trigger_key="always_no",
                    trigger_name="Always NO",
                    trigger_doc="Always returns NO decision.",
                    routes=TriggerRoutesDTO(),
                ),
            },
        )
        workflow_machine = StatefulWorkflow(
            workflow=workflow,
            trigger_factories={
                "always_yes": lambda: AlwaysYesTrigger(),
                "always_no": lambda: AlwaysNoTrigger(),
            },
        )

        graph = workflow_machine.get_graph(use_pygraphviz=False)

        self.assertIn(
            "state \"Always YES<br/>Always returns YES decision.\" as first",
            graph.source,
        )
        self.assertIn(
            "state \"Always NO<br/>Always returns NO decision.\" as second",
            graph.source,
        )
        self.assertIn("first --> second: go__first__second", graph.source)
        self.assertIn("direction TB", graph.source)

    def test_yes_no_and_default_routing(self) -> None:
        workflow = WorkflowDTO(
            start_node="check",
            nodes={
                "check": TriggerNodeDTO(
                    name="check",
                    trigger_key="contains_key",
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
                "contains_key": lambda: ContainsKeyTrigger(required_key="approved"),
                "always_yes": lambda: AlwaysYesTrigger(),
                "always_no": lambda: AlwaysNoTrigger(),
            },
        )

        yes_history = workflow_machine.run(
            self._ApprovedContext(approved=True),
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
                "contains_key": lambda: ContainsKeyTrigger(required_key="approved"),
                "always_yes": lambda: AlwaysYesTrigger(),
                "always_no": lambda: AlwaysNoTrigger(),
            },
        )

        history = workflow_machine.run(TriggerContextDTO())
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
                "always_yes": lambda: AlwaysYesTrigger(),
                "always_no": lambda: AlwaysNoTrigger(),
            },
        )

        history = workflow_machine.run(TriggerContextDTO())
        self.assertEqual([item.node for item in history], ["first", "second", "third"])
        self.assertEqual(workflow_machine.current_node, "third")

    def test_run_raises_on_cycle_when_max_steps_reached(self) -> None:
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
                    routes=TriggerRoutesDTO(no="first"),
                ),
            },
        )
        workflow_machine = StatefulWorkflow(
            workflow=workflow,
            trigger_factories={
                "always_yes": lambda: AlwaysYesTrigger(),
                "always_no": lambda: AlwaysNoTrigger(),
            },
        )

        with self.assertRaisesRegex(RuntimeError, "max_steps limit"):
            workflow_machine.run(TriggerContextDTO(), max_steps=4)


if __name__ == "__main__":
    unittest.main()
