"""Parent Entity."""
from __future__ import annotations

import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from .const import BBOX_NAME, DOMAIN, MANUFACTURER, CONF_HOST
from .coordinator import BboxDataUpdateCoordinator
from .helpers import finditem

_LOGGER = logging.getLogger(__name__)


class BboxEntity(CoordinatorEntity[BboxDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BboxDataUpdateCoordinator, description) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        device = finditem(coordinator.data, "info.device")
        self.box_id = device.get("serialnumber", "ABC12345")
        self._attr_unique_id = f"{self.box_id}-{description.key}"
        self.entity_description = description
        self._attr_device_info = {
            "identifiers": {(DOMAIN, self.box_id)},
            # "connections": {
            #     (
            #         CONNECTION_NETWORK_MAC,
            #         finditem(coordinator.data, "device_info.hosts.macaddress"),
            #     )
            # },
            "manufacturer": MANUFACTURER,
            "name": BBOX_NAME,
            "model": device.get("modelname"),
            "sw_version": device.get("main", {}).get("version"),
            "configuration_url": f"https://{coordinator.config_entry.data[CONF_HOST]}",
        }
