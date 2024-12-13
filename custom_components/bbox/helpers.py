"""Helpers for component."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True)
class BboxSensorDescription(SensorEntityDescription):
    """Describes a sensor."""

    get_value: Callable[..., Any] | None = None
    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class BboxBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a sensor."""

    value_fn: Callable[..., StateType] | None = None


def finditem(data: dict[str, Any], key_chain: str, default: Any = None) -> Any:
    """Get recursive key and return value.

    data is a mandatory dictonnary
    key , string with dot for key delimited (ex: "key.key.key")
    """
    if (keys := key_chain.split(".")) and isinstance(keys, list):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
    return default if data is None and default is not None else data
