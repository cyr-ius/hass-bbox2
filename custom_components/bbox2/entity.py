"""Parent Entity."""
from __future__ import annotations

import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import BBOX_NAME, DOMAIN, MANUFACTURER
from .coordinator import BboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class BboxEntity(CoordinatorEntity[BboxDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BboxDataUpdateCoordinator, description) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        device = coordinator.data.get("info", {}).get("device", {})
        sn = device.get("serialnumber", "ABC12345")

        self._attr_unique_id = f"{sn}-{description.key}"
        self._attr_name = description.key.capitalize().replace("_", " ")
        self.entity_description = description
        self._attr_device_info = {
            "identifiers": {(DOMAIN, sn)},
            "manufacturer": MANUFACTURER,
            "name": BBOX_NAME,
            "model": device.get("modelname"),
        }
