"""Tests for the Bbox sensor platform."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from bboxpy import BboxException, ServiceNotFoundError
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
    assert state.state == "176.0.0.0"

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


@pytest.mark.asyncio
async def test_temperature_from_cpu(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: Generator[AsyncMock | MagicMock],
):
    """Test the temperature falls back on the cpu data (F@st5688b)."""
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.bbox_system_temperature")
    assert state is not None
    # cpu.json reports 46407 m°C
    assert float(state.state) == 46.4


@pytest.mark.asyncio
async def test_sensors_missing_values(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: MagicMock,
):
    """Test the sensors do not fail when the Bbox does not report a value."""
    router.return_value.speedtest.async_get_speedtest_infos.return_value = [
        {"speedtest": {"latestmeasurements": {"download": [{"speed": None}]}}}
    ]
    router.return_value.device.async_get_bbox_cpu.side_effect = BboxException("404")

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert hass.states.get("sensor.bbox_ip_address").state == "176.0.0.0"
    assert hass.states.get("sensor.bbox_system_temperature").state == "unknown"


@pytest.mark.asyncio
async def test_speedtest_not_supported_requested_once(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    router: MagicMock,
):
    """Test an unsupported speedtest module is not requested at each refresh."""
    speedtest = router.return_value.speedtest.async_get_speedtest_infos
    speedtest.side_effect = ServiceNotFoundError(404, {})

    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    await config_entry.runtime_data.async_refresh()

    assert speedtest.await_count == 1
