"""Corddinator for Bbox."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from bboxpy import Bbox
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = 60


class BboxDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch datas."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
    ) -> None:
        """Class to manage fetching data API."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL)
        )
        self.bbox = Bbox(
            password=entry.data[CONF_PASSWORD],
            hostname=entry.data[CONF_HOST],
            session=async_create_clientsession(self.hass),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch datas."""
        try:
            bbox_info = self.check_list(await self.bbox.device.async_get_bbox_info())
            devices = self.check_list(await self.bbox.lan.async_get_connected_devices())
            wan_ip_stats = self.check_list(await self.bbox.wan.async_get_wan_ip_stats())
            # wan = self.check_list(await self.bbox.wan.async_get_wan_ip())
            # iptv_channels_infos = self.check_list(await self.bbox.iptv.async_get_iptv_info())
            # lan_stats = self.check_list(await self.bbox.lan.async_get_lan_stats())
            # voicemail = self.check_list(await self.bbox.voip.async_get_voip_voicemail())
            # device_info = self.check_list(await self.bbox.lan.async_get_device_infos())

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
        except Exception as error:
            _LOGGER.error(error)
            raise UpdateFailed from error

    @staticmethod
    def check_list(obj: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Return element if one only."""
        if isinstance(obj, list) and len(obj) == 1:
            return obj[0]
        else:
            raise UpdateFailed(
                "The call is not a list or it contains more than one element"
            )
