"""Corddinator for Bbox."""
from __future__ import annotations

import logging
from datetime import timedelta

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

    async def _async_update_data(self) -> dict:
        """Fetch datas."""
        try:
            rslt = await self.bbox.device.async_get_bbox_info()
            if len(rslt) == 1:
                bbox_info = rslt[0]
            else:
                bbox_info = rslt

            rslt = await self.bbox.lan.async_get_connected_devices()
            if len(rslt) == 1:
                devices = rslt[0]
            else:
                devices = rslt

            rslt = await self.bbox.wan.async_get_wan_ip_stats()
            if len(rslt) == 1:
                wan_ip_stats = rslt[0]
            else:
                wan_ip_stats = rslt

            # if (
            #     bbox_info.get("device", {}).get("adsl") == 1
            #     or bbox_info("device", {}).get("vdsl") == 1
            # ):
            #     physical_stats = await self.bbox.wan.async_get_wan_xdsl()
            # elif bbox_info("device", {}).get("ftth") == 1:
            #     physical_stats = await self.bbox.wan.async_get_wan_ftth()
            # else:
            #     physical_stats = {}

            return {
                "info": bbox_info,
                "devices": devices,
                "wan_ip_stats": wan_ip_stats,
                # "wan": await self.bbox.wan.async_get_wan_ip(),
                # "physical_stats": physical_stats,
                # "iptv_channels_infos": await self.bbox.iptv.async_get_iptv_info(),
                # "lan_stats": await self.bbox.lan.async_get_lan_stats(),
                # "voicemail": await self.bbox.lan.async_get_voip_voicemail(),
                # "physical_support": physical_support
            }
        except Exception as error:
            _LOGGER.error(error)
            raise UpdateFailed from error
