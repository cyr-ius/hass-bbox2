"""Corddinator for Bbox."""
from __future__ import annotations

import logging
from datetime import timedelta

from bboxpy import Bbox

from homeassistant.core import HomeAssistant
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
            password=entry.data[CONF_PASSWORD], hostname=entry.data[CONF_HOST]
        )

    async def _async_update_data(self) -> dict:
        """Fetch datas."""
        try:
            return {
                "info": await self.bbox.device.get_bbox_info(),
                "devices": await self.bbox.lan.async_get_connected_devices(),
                "stats": await self.bbox.wan.async_get_wan_ip_stats(),
            }
        except Exception as error:
            _LOGGER.error(error)
            raise UpdateFailed from error
