"""The tests for the bbox component."""

from unittest.mock import AsyncMock, patch

import pytest

from .const import (
    DEVICES,
    INFO,
    LEDS,
    MEM,
    PARENTALCONTROL,
    SPEEDTEST_INFOS,
    WAN_IP,
    WAN_IP_STATS,
    WIFI,
    WPS,
)


@pytest.fixture(name="router")
def mock_router():
    """Mock a successful connection."""
    with patch("config.custom_components.bbox.coordinator.Bbox") as mock:
        instance = mock.return_value
        instance.open = AsyncMock()
        instance.device.async_get_bbox_info = AsyncMock(return_value=INFO)
        instance.device.async_get_bbox_mem = AsyncMock(return_value=MEM)
        instance.device.async_get_bbox_leds = AsyncMock(return_value=LEDS)
        instance.lan.asycn_get_connected_devices = AsyncMock(return_value=DEVICES)
        instance.wan.async_get_wan_ip_stats = AsyncMock(return_value=WAN_IP_STATS)
        instance.parentalcontrol.async_get_parental_control = AsyncMock(
            return_value=PARENTALCONTROL
        )
        instance.wifi.async_get_wps = AsyncMock(return_value=WPS)
        instance.wifi.async_get_wireless = AsyncMock(return_value=WIFI)
        instance.wan.async_get_wan_ip = AsyncMock(return_value=WAN_IP)
        instance.speedtest.async_get_speedtest_infos = AsyncMock(
            return_value=SPEEDTEST_INFOS
        )
        instance.close = AsyncMock()
        yield mock
