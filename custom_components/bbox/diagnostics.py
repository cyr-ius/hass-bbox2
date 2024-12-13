"""Diagnostics support."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import TO_REDACT


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    _datas = {}

    async def diag(func: Callable[..., Any], *args: Any) -> None:
        rslt = {}
        with suppress(Exception):
            rsp = await func(*args)
            rslt = (
                rsp
                if isinstance(rsp, dict | list | set | float | int | str | tuple)
                else vars(rsp)
            )

        _datas.update({func.__name__: rslt})

    await diag(coordinator.bbox.device.async_get_bbox_info)
    await diag(coordinator.bbox.lan.async_get_connected_devices)
    await diag(coordinator.bbox.wan.async_get_wan_ip)
    await diag(coordinator.bbox.iptv.async_get_iptv_info)
    await diag(coordinator.bbox.lan.async_get_lan_stats)
    await diag(coordinator.bbox.voip.async_get_voip_voicemail)
    await diag(coordinator.bbox.lan.async_get_device_infos)

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(coordinator.data, TO_REDACT),
        "raw": async_redact_data(_datas, TO_REDACT),
    }
