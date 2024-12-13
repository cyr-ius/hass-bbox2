"""Button for Bbox router."""

import asyncio
import logging

from typing import Any

from bboxpy.exceptions import BboxException

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BBoxConfigEntry, BboxDataUpdateCoordinator
from .entity import BboxEntity, BboxDeviceEntity
from .helpers import finditem

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data
    description = SwitchEntityDescription(
        key="parental_control",
        translation_key="parental_control",
        name="Parental control",
        icon="mdi:security"
    )
    devices = coordinator.data.get("devices", {}).get("hosts", {}).get("list", [])
    entities = [
        DeviceParentalControlSwitch(coordinator, description, device)
        for device in devices
        if device.get("macaddress")
    ]
    entities += [ParentalControlServiceSwitch(coordinator, description)]
    async_add_entities(entities)


class ParentalControlServiceSwitch(BboxEntity, SwitchEntity):
    """Representation of a switch for Bbox parental control service state."""
    
    waiting_delay_after_toggle = 5

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: SwitchEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)

        self._attr_name = "Parental control"

    @property
    def is_on(self) -> bool:
        """Return true if parental control service is currently enabled."""
        return bool(
            finditem(self.coordinator.data, "parentalcontrol.parentalcontrol.scheduler.enable")
        )

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.bbox.parentalcontrol.async_set_parental_control_service_state(
                enable=True
            )
        except BboxException as error:
            _LOGGER.error(error)
            return
        _LOGGER.debug(
            "Request sent, we need to wait a bit (%ds) before updating state...",
            self.waiting_delay_after_toggle
        )
        await asyncio.sleep(self.waiting_delay_after_toggle)
        _LOGGER.debug("Updating state")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.bbox.parentalcontrol.async_set_parental_control_service_state(
                enable=False
            )
        except BboxException as error:
            _LOGGER.error(error)
            return
        _LOGGER.debug(
            "Request sent, we need to wait a bit (%ds) before updating state...",
            self.waiting_delay_after_toggle
        )
        await asyncio.sleep(self.waiting_delay_after_toggle)
        _LOGGER.debug("Updating state")
        await self.coordinator.async_request_refresh()


class DeviceParentalControlSwitch(BboxDeviceEntity, SwitchEntity):
    """Representation of a switch for device parental control state."""

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: SwitchEntityDescription,
        device: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description, device)

        self._attr_name = "Parental control"
        self._attr_unique_id = f"{self._device_key}_parental_control"

    @property
    def is_on(self) -> bool:
        """Return true if device parental control is currently enabled."""
        return bool(finditem(self.coordinator_data, "parentalcontrol.enable"))

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        try:
            await self.coordinator.bbox.parentalcontrol.async_set_device_parental_control_state(
                macaddress= self._device["macaddress"],
                enable=True
            )
        except BboxException as error:
            _LOGGER.error(error)
            return
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        try:
            await self.coordinator.bbox.parentalcontrol.async_set_device_parental_control_state(
                macaddress= self._device["macaddress"],
                enable=False
            )
        except BboxException as error:
            _LOGGER.error(error)
            return
        await self.coordinator.async_request_refresh()
        
