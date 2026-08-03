"""Tests pour l'intégration Bbox2 utilisant config_entries."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant


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
