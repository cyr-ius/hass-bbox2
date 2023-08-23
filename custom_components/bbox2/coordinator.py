"""Corddinator for Bbox."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from pybbox2 import Bbox

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
            password=entry.data[CONF_PASSWORD], api_host=entry.data[CONF_HOST]
        )

    def _sync_update(self) -> dict[str, dict[str, Any]]:
        return {
            "info": self.bbox.get_bbox_info(),
            "devices": self.bbox.get_all_connected_devices(),
            "stats": self.bbox.get_ip_stats(),
        }

    async def _async_update_data(self) -> dict:
        """Fetch datas."""
        try:
            return await self.hass.async_add_executor_job(self.bbox.get_bbox_info)
        except Exception as error:
            _LOGGER.error(error)
            raise UpdateFailed from error
