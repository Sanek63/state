from __future__ import annotations

from punq import Container

from .engine import TriggerFactory
from .triggers import BaseTrigger


def attach_trigger_mapping(
    container: Container,
    trigger_mapping: dict[str, type[BaseTrigger]],
) -> None:
    for trigger_key, trigger_type in trigger_mapping.items():
        container.register(trigger_key, trigger_type)


def create_container(
    trigger_mapping: dict[str, type[BaseTrigger]],
) -> Container:
    container = Container()
    attach_trigger_mapping(container, trigger_mapping)
    return container


def build_trigger_factories(
    container: Container,
    trigger_mapping: dict[str, type[BaseTrigger]],
) -> dict[str, TriggerFactory]:
    return {
        trigger_key: (lambda trigger_key=trigger_key: container.resolve(trigger_key))
        for trigger_key in trigger_mapping
    }
