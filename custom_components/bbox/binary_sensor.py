"""Support for Bbox binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import BBoxConfigEntry
from .entity import BboxEntity
from .helpers import finditem


@dataclass(frozen=True)
class BboxBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a sensor."""

    get_value: Callable[..., Any] | None = None
    value_fn: Callable[..., StateType] | None = None


BINARIES_SENSORS: tuple[BboxBinarySensorDescription, ...] = (
    BboxBinarySensorDescription(
        key="info.device.status",
        name="Link status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda x: x == 1,
    ),
    BboxBinarySensorDescription(
        key="led.ethernetPort.0.state",
        name="Ethernet port 1",
        value_fn=lambda x: x.lower() == "up",
        entity_registry_enabled_default=False,
    ),
    BboxBinarySensorDescription(
        key="led.ethernetPort.1.state",
        name="Ethernet port 2",
        value_fn=lambda x: x.lower() == "up",
        entity_registry_enabled_default=False,
    ),
    BboxBinarySensorDescription(
        key="led.ethernetPort.2.state",
        name="Ethernet port 3",
        value_fn=lambda x: x.lower() == "up",
        entity_registry_enabled_default=False,
    ),
    BboxBinarySensorDescription(
        key="led.ethernetPort.3.state",
        name="Ethernet port 4",
        value_fn=lambda x: x.lower() == "up",
        entity_registry_enabled_default=False,
    ),
    BboxBinarySensorDescription(
        key="led.ethernetPort.4.state",
        name="Ethernet port 5",
        value_fn=lambda x: x.lower() == "up",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    entities = [
        BboxBinarySensor(coordinator, description) for description in BINARIES_SENSORS
    ]
    async_add_entities(entities)


class BboxBinarySensor(BboxEntity, BinarySensorEntity):
    """Representation of a sensor."""

    @property
    def is_on(self):
        """Return sensor state."""
        data = finditem(self.coordinator.data, self.entity_description.key)
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(data)
        return data
