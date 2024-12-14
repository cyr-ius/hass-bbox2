"""Support for Bbox binary sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

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

    value_fn: Callable[..., StateType] | None = None


BINARIES_SENSORS: tuple[BboxBinarySensorDescription, ...] = (
    BboxBinarySensorDescription(
        key="info.device.status",
        name="Link status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda x: x == 1,
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
