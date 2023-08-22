"""Support for Bbox binary sensors."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BboxEntity

SENSOR_TYPES: tuple[BinarySensorEntityDescription, ...] = (
    BinarySensorEntityDescription(
        key="ipv4",
        name="IPV4 Enabled",
    ),
    BinarySensorEntityDescription(
        key="ipv6",
        name="IPV6 Enabled",
    ),
    BinarySensorEntityDescription(
        key="ftth",
        name="FTTH enabled",
    ),
    BinarySensorEntityDescription(
        key="adsl",
        name="Adsl",
    ),
    BinarySensorEntityDescription(
        key="vdsl",
        name="Vdsl",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for description in SENSOR_TYPES:
        entities.append(BboxSensor(coordinator, description))

    async_add_entities(entities)


class BboxSensor(BboxEntity, BinarySensorEntity):
    """Representation of a sensor."""

    @property
    def is_on(self):
        """Return sensor state."""
        device = self.coordinator.data["info"]["device"]
        return device[self.entity_description.key] == 1
