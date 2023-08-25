"""Support for Bbox binary sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BboxEntity
from .helpers import BboxBinarySensorDescription, finditem

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[BboxBinarySensorDescription, ...] = (
    BboxBinarySensorDescription(
        key="info.device.status",
        name="Link status",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda x: x == 1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        BboxBinarySensor(coordinator, description) for description in SENSOR_TYPES
    ]

    async_add_entities(entities)


class BboxBinarySensor(BboxEntity, BinarySensorEntity):
    """Representation of a sensor."""

    @property
    def is_on(self):
        """Return sensor state."""
        _LOGGER.debug("%s %s", self.name, self.entity_description.key)
        data = finditem(self.coordinator.data, self.entity_description.key)
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(data)
        return data
