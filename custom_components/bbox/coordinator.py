"""Corddinator for Bbox."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from bboxpy import AuthorizationError, Bbox, BboxException, ServiceNotFoundError
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_REFRESH_RATE, CONF_USE_TLS, DEFAULT_REFRESH_RATE, DOMAIN

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
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=entry.options.get(CONF_REFRESH_RATE, DEFAULT_REFRESH_RATE)
            ),
        )
        self.entry = entry
        self._speedtest_supported = True

    async def _async_setup(self) -> None:
        """Start Bbox connection."""
        try:
            self.bbox = Bbox(
                password=self.entry.data[CONF_PASSWORD],
                hostname=self.entry.data[CONF_HOST],
                use_tls=self.entry.data.get(CONF_USE_TLS, False),
                verify_ssl=self.entry.data.get(CONF_VERIFY_SSL, False),
            )
        except AuthorizationError as error:
            raise ConfigEntryAuthFailed(
                f"Password expired for {self.entry.data[CONF_HOST]}"
            ) from error

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data."""
        try:
            bbox_info = self.check_list(await self.bbox.device.async_get_bbox_info())
            memory = self.check_list(
                await self._call(self.bbox.device.async_get_bbox_mem)
            )
            led = self.check_list(await self._call(self.bbox.device.async_get_bbox_led))
            devices = await self._call(self.bbox.lan.async_get_connected_devices)
            wan_ip_stats = self.check_list(
                await self._call(self.bbox.wan.async_get_wan_ip_stats)
            )
            parentalcontrol = self.check_list(
                await self._call(
                    self.bbox.parentalcontrol.async_get_parental_control_service_state
                )
            )
            wps = self.check_list(await self._call(self.bbox.wifi.async_get_wps))
            wifi = self.check_list(await self._call(self.bbox.wifi.async_get_wireless))
            wan_ip = self.check_list(await self._call(self.bbox.wan.async_get_wan_ip))
        except BboxException as error:
            _LOGGER.error(error)
            raise UpdateFailed from error

        cpu = await self._async_get_optional(self.bbox.device.async_get_bbox_cpu)
        speedtest_infos = await self._async_get_speedtest_infos()

        return {
            "info": bbox_info,
            "cpu": cpu,
            "memory": memory,
            "led": led,
            "devices": self.merge_objects(devices),
            "wan_ip_stats": wan_ip_stats,
            "parentalcontrol": parentalcontrol,
            "wps": wps,
            "wifi": wifi,
            "wan_ip": wan_ip,
            "speedtest_infos": speedtest_infos,
        }

    async def _async_get_optional(self, func: Callable[..., Any]) -> dict[str, Any]:
        """Execute a request which may be unsupported by the Bbox model."""
        try:
            result = await func()
        except BboxException as error:
            _LOGGER.debug("Error while execute: %s (%s)", func.__name__, error)
            return {}
        if (
            isinstance(result, list)
            and len(result) == 1
            and isinstance(result[0], dict)
        ):
            return result[0]
        return {}

    async def _async_get_speedtest_infos(self) -> dict[str, Any]:
        """Return the speedtest data, not requested anymore once known unsupported."""
        if not self._speedtest_supported:
            return {}
        try:
            return self.check_list(
                await self.bbox.speedtest.async_get_speedtest_infos()
            )
        except ServiceNotFoundError as error:
            self._speedtest_supported = False
            _LOGGER.info(
                "SpeedTest module is not available on this Bbox (%s), it will not be requested anymore",
                error,
            )
        except BboxException as error:
            _LOGGER.debug("Unable to get the SpeedTest data (%s)", error)
        return {}

    @staticmethod
    def merge_objects(objs: Any) -> dict[str, Any]:
        """Merge objects return by the Bbox API."""
        assert isinstance(objs, list)

        def merge(a: dict, b: dict, path: list[str] | None = None):
            path = path or []
            for key, value in b.items():
                if key in a:
                    if isinstance(a[key], dict) and isinstance(value, dict):
                        merge(a[key], value, path + [str(key)])
                    elif isinstance(a[key], list) and isinstance(value, list):
                        a[key].extend(value)
                    elif a[key] != value:
                        raise ValueError(
                            f"Conflict merging the key {'.'.join(path + [str(key)])} of the "
                            "objects return by the Bbox API: "
                            f"'{a[key]}' ({type(a[key])}) != '{value}' ({type(value)})"
                        )
                else:
                    a[key] = value
            return a

        result = objs[0]
        assert isinstance(result, dict), (
            f"The first element of the list is not a dict (but {type(result)}): {result}"
        )
        for idx, obj in enumerate(objs[1:]):
            assert isinstance(obj, dict), (
                f"The {idx + 2} element of the list is not a dict (but {type(obj)}): {obj}"
            )
            result = merge(result, obj)
        return result

    @staticmethod
    def check_list(obj: Any) -> dict[str, Any]:
        """Return element if one only."""
        if not isinstance(obj, list):
            raise UpdateFailed(f"The call is not a list ({type(obj)}): {obj}")
        if len(obj) != 1:
            raise UpdateFailed(
                f"The call contains more than one element ({len(obj)}): {obj}"
            )
        return obj[0]

    async def _call(self, func: Callable[..., Any], *args: Any) -> dict[str, Any]:
        """Execute request."""
        try:
            return await func(*args)
        except BboxException as error:
            _LOGGER.warning("Error while execute: %s (%s)", func.__name__, error)
        return {}
