"""Tests for the Bbox sensor platform."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


@pytest.mark.asyncio
async def test_sensors_state(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: Generator[AsyncMock | MagicMock],
):
    """Test the state of various sensors."""
    # Setup the integration
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    # --- Test IP Address Sensor (simple value from API) ---
    # This sensor directly reflects the value from the API
    state = hass.states.get("sensor.bbox_ip_address")
    assert state is not None
    assert state.state == "176.186.46.71"

    # --- Test Downloaded Sensor (value processed by a function) ---
    # This sensor's value is calculated from the API data
    state = hass.states.get("sensor.bbox_downloaded")
    assert state is not None
    # From wan_ip_stats.json, rx.bytes is "602044620".
    # The value_fn is lambda x: round(float(x) / 1000, 2) -> 602044.62
    assert float(state.state) == 602044.62

    # --- Test Memory Free Sensor (value calculated from multiple API data points) ---
    # This sensor's value is computed using a custom get_value function
    state = hass.states.get("sensor.bbox_memory_free")
    assert state is not None
    # From memory.json, free is 114310 and total is 214000.
    # The get_value function calculates (free * 100) / total
    assert float(state.state) == 53.4245373658048
