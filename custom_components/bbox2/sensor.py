"""Support for Bbox sensors."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate, UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BboxEntity
from .helpers import BboxSensorDescription, finditem

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[BboxSensorDescription, ...] = (
    BboxSensorDescription(
        key="info.device.temperature.current",
        name="System Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.rx.bytes",
        name="Download speed",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        icon="mdi:download-network",
        value_fn=lambda x: round(x / 1000000, 2),
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.rx.packetsdiscards",
        name="Download discard packet",
        icon="mdi:upload-network",
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.rx.packetserrors",
        name="Download error packet",
        icon="mdi:upload-network",
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.rx.occupation",
        name="Download bandwidth occupation (%)",
        device_class=SensorDeviceClass.DATA_RATE,
        icon="mdi:upload-network",
        value_fn=lambda x: float(x),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.bytes",
        name="Upload speed",
        device_class=SensorDeviceClass.DATA_RATE,
        native_unit_of_measurement=UnitOfDataRate.KILOBYTES_PER_SECOND,
        icon="mdi:upload-network",
        value_fn=lambda x: round(x / 1000000, 2),
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.packetsdiscards",
        name="Upload discard packet",
        icon="mdi:upload-network",
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.packetserrors",
        name="Upload error packet",
        icon="mdi:upload-network",
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.occupation",
        name="Upload bandwidth occupation (%)",
        device_class=SensorDeviceClass.DATA_RATE,
        icon="mdi:upload-network",
        value_fn=lambda x: float(x),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [BboxSensor(coordinator, description) for description in SENSOR_TYPES]
    async_add_entities(entities)


class BboxSensor(BboxEntity, SensorEntity):
    """Representation of a sensor."""

    @property
    def native_value(self):
        """Return sensor state."""
        data = finditem(self.coordinator.data, self.entity_description)
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(data)
        return data
