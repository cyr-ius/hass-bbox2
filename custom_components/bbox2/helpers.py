"""Helpers for component."""
from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.binary_sensor import BinarySensorEntityDescription


@dataclass
class BboxValueFnMixin:
    """Mixin for Audi sensor."""

    value_fn: Callable[..., StateType] | None = None


@dataclass
class BboxSensorDescription(BboxValueFnMixin, SensorEntityDescription):
    """Describes a sensor."""


@dataclass
class BboxBinarySensorDescription(BboxValueFnMixin, BinarySensorEntityDescription):
    """Describes a sensor."""


def finditem(data, entity_description):
    if (keys := entity_description.key.split(".")) and isinstance(keys, list):
        for key in keys:
            if isinstance(data, dict):
                data = data.get(key)
    return data
