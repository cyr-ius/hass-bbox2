"""Tests pour l'intégration Bbox2 utilisant config_entries."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr


@pytest.mark.asyncio
async def test_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: Generator[AsyncMock | MagicMock],
) -> None:
    """Test du setup via une config entry."""

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED


@pytest.mark.asyncio
async def test_track_devices_option(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: Generator[AsyncMock | MagicMock],
) -> None:
    """Test the device trackers are not created when the option is disabled."""
    hass.config_entries.async_update_entry(
        config_entry, options={"track_devices": False}
    )
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state == ConfigEntryState.LOADED
    assert not hass.states.async_entity_ids("device_tracker")


@pytest.mark.asyncio
async def test_connected_devices_are_linked_to_the_box(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: Generator[AsyncMock | MagicMock],
) -> None:
    """Test the connected devices use via_device_id to reference the Bbox."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(registry, config_entry.entry_id)
    box_ids = {d.id for d in devices if d.via_device_id is None}
    children = [d for d in devices if d.via_device_id is not None]

    assert len(box_ids) == 1
    assert children
    assert all(d.via_device_id in box_ids for d in children)
