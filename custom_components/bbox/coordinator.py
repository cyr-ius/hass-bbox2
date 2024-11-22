"""Corddinator for Bbox."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from bboxpy import Bbox

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_DEFAULTS, CONF_HOST, CONF_PASSWORD, CONF_USE_TLS, DOMAIN, CONF_REFRESH_RATE

_LOGGER = logging.getLogger(__name__)


class BboxDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch data."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
    ) -> None:
        """Class to manage fetching data API."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.data.get(CONF_REFRESH_RATE, CONF_DEFAULTS[CONF_REFRESH_RATE])
            )
        )
        self.entry = entry

    async def connect(self):
        """Start Bbox connection"""
        self.bbox = Bbox(
            password=self.entry.data[CONF_PASSWORD],
            hostname=self.entry.data[CONF_HOST],
            session=async_create_clientsession(self.hass),
            use_tls=self.entry.data.get(CONF_USE_TLS, False),
        )

    async def update_configuration(self, hass, entry):
        """Update configuration"""
        self.entry = entry
        await self.connect()

        self.update_interval = timedelta(
            seconds=entry.data[CONF_REFRESH_RATE]
        )
        _LOGGER.debug("Coordinator refresh interval updated (%s)", self.update_interval)

        _LOGGER.debug("Force update")
        await self.async_refresh()

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data."""
        try:
            bbox_info = self.check_list(await self.bbox.device.async_get_bbox_info())
            devices = self.check_list(await self.bbox.lan.async_get_connected_devices())
            wan_ip_stats = self.check_list(await self.bbox.wan.async_get_wan_ip_stats())
            # wan = self.check_list(await self.bbox.wan.async_get_wan_ip())
            # iptv_channels_infos = self.check_list(await self.bbox.iptv.async_get_iptv_info())
            # lan_stats = self.check_list(await self.bbox.lan.async_get_lan_stats())
            # voicemail = self.check_list(await self.bbox.voip.async_get_voip_voicemail())
            # device_info = self.check_list(await self.bbox.lan.async_get_device_infos())
        except Exception as error:
            _LOGGER.error(error)
            raise UpdateFailed from error

        return {
            "info": bbox_info,
            "devices": devices,
            "wan_ip_stats": wan_ip_stats,
            # "wan": wan,
            # "iptv_channels_infos": iptv_channels_infos,
            # "lan_stats": lan_stats,
            # "voicemail": voicemail,
            # "device_info": device_info,
        }

    @staticmethod
    def check_list(obj: Any) -> dict[str, Any]:
        """Return element if one only."""
        if isinstance(obj, list) and len(obj) == 1:
            return obj[0]

        raise UpdateFailed(
            "The call is not a list or it contains more than one element"
        )
