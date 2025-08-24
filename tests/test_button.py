"""The tests for the bbox component."""

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion


async def test_reboot(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    router,
) -> None:
    """Test reboot button."""

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    data = {
        ATTR_ENTITY_ID: "button.restart",
    }

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        service_data=data,
        blocking=True,
    )
    await hass.async_block_till_done()
