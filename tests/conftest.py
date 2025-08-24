"""The tests for the bbox component."""

from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER, ConfigEntry
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bbox.const import DOMAIN

from .const import (
    DEVICES,
    INFO,
    LEDS,
    MEM,
    MOCK_USER_INPUT,
    PARENTALCONTROL,
    SPEEDTEST_INFOS,
    WAN_IP,
    WAN_IP_STATS,
    WIFI,
    WPS,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for hass."""
    yield


@pytest.fixture(name="router")
def mock_router() -> Generator[MagicMock | AsyncMock]:
    """Mock a successful connection."""
    with patch("custom_components.bbox.coordinator.Bbox") as mock:
        instance = mock.return_value
        instance.open = AsyncMock()
        instance.async_login = AsyncMock(return_value=True)
        instance.device.async_get_bbox_info = AsyncMock(return_value=INFO)
        instance.device.async_get_bbox_mem = AsyncMock(return_value=MEM)
        instance.device.async_get_bbox_led = AsyncMock(return_value=LEDS)
        instance.device.async_reboot = AsyncMock()
        instance.lan.async_get_connected_devices = AsyncMock(return_value=DEVICES)
        instance.wan.async_get_wan_ip_stats = AsyncMock(return_value=WAN_IP_STATS)
        instance.parentalcontrol.async_get_parental_control_service_state = AsyncMock(
            return_value=PARENTALCONTROL,
        )
        instance.parentalcontrol.async_set_parental_control_service_state = AsyncMock()
        instance.parentalcontrol.async_set_device_parental_control_state = AsyncMock()
        instance.wifi.async_get_wps = AsyncMock(return_value=WPS)
        instance.wifi.async_get_wireless = AsyncMock(return_value=WIFI)
        instance.wan.async_get_wan_ip = AsyncMock(return_value=WAN_IP)
        instance.wps.async_on_wps = AsyncMock()
        instance.wps.async_off_wps = AsyncMock()
        instance.wifi.async_set_wireless = AsyncMock()
        instance.wifi.async_set_wireless_24 = AsyncMock()
        instance.wifi.async_set_wireless_5 = AsyncMock()
        instance.wifi.async_set_wireless_guest = AsyncMock()
        instance.speedtest.async_get_speedtest_infos = AsyncMock(
            return_value=SPEEDTEST_INFOS
        )
        instance.close = AsyncMock()
        yield mock


@pytest.fixture(name="config_entry")
def get_config_entry(hass: HomeAssistant) -> ConfigEntry:
    """Create and register mock config entry."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        source=SOURCE_USER,
        data=MOCK_USER_INPUT,
        unique_id="1",
        options={},
        entry_id="123456",
    )
    config_entry.add_to_hass(hass)
    return config_entry
