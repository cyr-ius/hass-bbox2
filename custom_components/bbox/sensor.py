"""Support for Bbox sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfDataRate, UnitOfInformation, UnitOfTemperature, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BBoxConfigEntry
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
        name="Downloaded",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KILOBITS,
        icon="mdi:download-network",
        value_fn=lambda x: round(float(x) / 1000, 2),
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
        key="wan_ip_stats.wan.ip.stats.rx.bandwidth",
        name="Download speed",
        device_class=SensorDeviceClass.DATA_RATE,
        icon="mdi:upload-network",
        value_fn=lambda x: float(x),
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.rx.occupation",
        name="Download bandwidth occupation",
        device_class=SensorDeviceClass.POWER_FACTOR,
        icon="mdi:upload-network",
        get_value=lambda self: (
            float(finditem(self.coordinator.data, "wan_ip_stats.wan.ip.stats.rx.bandwidth")) * 100 /
            float(finditem(self.coordinator.data, "wan_ip_stats.wan.ip.stats.rx.maxBandwidth"))
        ),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.bytes",
        name="Uploaded",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.KILOBITS,
        icon="mdi:upload-network",
        value_fn=lambda x: round(float(x) / 1000, 2),
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
        key="wan_ip_stats.wan.ip.stats.tx.bandwidth",
        name="Upload speed",
        device_class=SensorDeviceClass.DATA_RATE,
        icon="mdi:upload-network",
        value_fn=lambda x: float(x),
        native_unit_of_measurement=UnitOfDataRate.KILOBITS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BboxSensorDescription(
        key="wan_ip_stats.wan.ip.stats.tx.occupation",
        name="Upload bandwidth occupation",
        device_class=SensorDeviceClass.POWER_FACTOR,
        icon="mdi:upload-network",
        get_value=lambda self: (
            float(finditem(self.coordinator.data, "wan_ip_stats.wan.ip.stats.tx.bandwidth")) * 100 /
            float(finditem(self.coordinator.data, "wan_ip_stats.wan.ip.stats.tx.maxBandwidth"))
        ),
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    entities = [BboxSensor(coordinator, description) for description in SENSOR_TYPES]
    async_add_entities(entities)


class BboxSensor(BboxEntity, SensorEntity):
    """Representation of a sensor."""

    @property
    def native_value(self):
        """Return sensor state."""
        raw_value = (
            self.entity_description.get_value(self)
            if self.entity_description.get_value is not None
            else finditem(self.coordinator.data, self.entity_description.key)
        )
        return (
            self.entity_description.value_fn(raw_value)
            if self.entity_description.value_fn is not None
            else raw_value
        )
