"""The Bouygues Bbox integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import BBOX_NAME, DOMAIN, MANUFACTURER
from .coordinator import BboxDataUpdateCoordinator
from .helpers import finditem

type BBoxConfigEntry = ConfigEntry[BboxDataUpdateCoordinator]

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.BUTTON,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: BBoxConfigEntry) -> bool:
    """Set up Bouygues Bbox from a config entry."""
    coordinator = BboxDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    # The Bbox device must exist before the devices connected to it (via_device_id)
    device = finditem(coordinator.data, "info.device")
    dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, device.get("serialnumber", "ABC12345"))},
        manufacturer=MANUFACTURER,
        name=BBOX_NAME,
        model=device.get("modelname"),
        sw_version=device.get("main", {}).get("version"),
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def _async_update_listener(hass: HomeAssistant, entry: BBoxConfigEntry) -> None:
    """Reload the entry when the options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: BBoxConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: BBoxConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove config entry from a device."""
    return True
