"""Config flow for Bouygues Bbox integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from bboxpy import Bbox
from bboxpy.exceptions import HttpRequestError

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import BBOX_URL, CONF_HOST, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=BBOX_URL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bouygues Bbox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                bbox = Bbox(
                    hostname=user_input[CONF_HOST],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                )
                await bbox.async_login()
                # info = await bbox.device.async_get_bbox_summary()
                # await self.async_set_unique_id(
                #     info.get("device", {}).get("serialnumber", "ABC12345")
                # )
                # self._abort_if_unique_id_configured()
            except (HttpRequestError, CannotConnect):
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="Bouygues Bbox", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
