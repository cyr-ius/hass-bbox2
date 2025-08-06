"""Button for Bbox router."""

import asyncio
from dataclasses import dataclass
import logging
from typing import Any, Final

from bboxpy.exceptions import BboxException

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BBoxConfigEntry, BboxDataUpdateCoordinator
from .entity import BboxDeviceEntity, BboxEntity
from .helpers import finditem


@dataclass(frozen=True)
class BboxSwitchEntityDescription(SwitchEntityDescription):
    """Represents an Flow Sensor."""

    state: str | None = None
    api: str | None = None
    turn_on: str | None = None
    turn_off: str | None = None


SWITCH_TYPES: Final[tuple[BboxSwitchEntityDescription, ...]] = (
    BboxSwitchEntityDescription(
        key="parental_control",
        translation_key="parental_control",
        name="Parental control",
        icon="mdi:security",
        state="parentalcontrol.parentalcontrol.scheduler.enable",
        api="parentalcontrol",
        turn_on="async_set_parental_control_service_state",
        turn_off="async_set_parental_control_service_state",
    ),
    BboxSwitchEntityDescription(
        key="wps",
        translation_key="wps",
        name="Wps",
        state="wps.wps.enable",
        api="wps",
        turn_on="async_on_wps",
        turn_off="async_off_wps",
    ),
    BboxSwitchEntityDescription(
        key="wifi_24",
        translation_key="wifi_24",
        name="Wifi 2.4Ghz",
        state="wifi.wireless.radio.24.enable",
        api="wifi",
        turn_on="async_set_wireless_24",
        turn_off="async_set_wireless_24",
    ),
    BboxSwitchEntityDescription(
        key="wifi_5",
        translation_key="wifi_5",
        name="Wifi 5Ghz",
        state="wifi.wireless.radio.5.enable",
        api="wifi",
        turn_on="async_set_wireless_5",
        turn_off="async_set_wireless_5",
    ),
    BboxSwitchEntityDescription(
        key="wifi_guest",
        translation_key="wifi_guest",
        name="Wifi Guest",
        state="wifi.wireless.radio.guest.enable",
        api="wifi",
        turn_on="async_set_wireless_guest",
        turn_off="async_set_wireless_guest",
    ),
)

SWITCHE_DEVICES = BboxSwitchEntityDescription(
    key="parental_control",
    translation_key="parental_control",
    name="Parental control",
    state="parentalcontrol.enable",
    icon="mdi:security",
    api="parentalcontrol",
    turn_on="async_set_device_parental_control_state",
    turn_off="async_set_device_parental_control_state",
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: BBoxConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = entry.runtime_data

    devices = coordinator.data.get("devices", {}).get("hosts", {}).get("list", [])
    entities = [
        DeviceParentalControlSwitch(coordinator, SWITCHE_DEVICES, device)
        for device in devices
        if device.get("macaddress")
    ]
    entities += [BboxSwitch(coordinator, description) for description in SWITCH_TYPES]
    async_add_entities(entities)


class BboxSwitch(BboxEntity, SwitchEntity):
    """Representation of a switch for Bbox."""

    waiting_delay_after_toggle = 5

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: BboxSwitchEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description)

    @property
    def is_on(self) -> bool:
        """Return state."""
        return bool(finditem(self.coordinator.data, self.entity_description.state))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        kwargs = kwargs or {"enable": True}
        try:
            await getattr(
                getattr(self.coordinator.bbox, self.entity_description.api),
                self.entity_description.turn_on,
            )(**kwargs)
        except BboxException as error:
            _LOGGER.error(error)
        else:
            await asyncio.sleep(self.waiting_delay_after_toggle)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        kwargs = kwargs or {"enable": False}
        try:
            await getattr(
                getattr(self.coordinator.bbox, self.entity_description.api),
                self.entity_description.turn_off,
            )(**kwargs)
        except BboxException as error:
            _LOGGER.error(error)
        else:
            await asyncio.sleep(self.waiting_delay_after_toggle)
            await self.coordinator.async_request_refresh()


class DeviceParentalControlSwitch(BboxDeviceEntity, BboxSwitch):
    """Representation of a switch for device parental control state."""

    def __init__(
        self,
        coordinator: BboxDataUpdateCoordinator,
        description: BboxSwitchEntityDescription,
        device: dict[str, Any],
    ) -> None:
        """Initialize."""
        super().__init__(coordinator, description, device)

        self._attr_unique_id = f"{self._device_key}_parental_control"

    @property
    def is_on(self) -> bool:
        """Return true if device parental control is currently enabled."""
        return bool(finditem(self._device, self.entity_description.state))

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await super().async_turn_on(macaddress=self._device["macaddress"], enable=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await super().async_turn_off(
            macaddress=self._device["macaddress"], enable=False
        )
