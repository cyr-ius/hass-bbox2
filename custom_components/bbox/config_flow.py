"""Config flow for Bouygues Bbox integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from bboxpy import Bbox
from bboxpy.exceptions import BboxException, HttpRequestError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import BBOX_URL, CONF_HOST, CONF_PASSWORD, CONF_USE_TLS, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=BBOX_URL): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_USE_TLS, default=True): bool,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bouygues Bbox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input:
            try:
                api = Bbox(
                    hostname=user_input[CONF_HOST],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                    use_tls=user_input[CONF_USE_TLS],
                )
                await api.async_login()
                infos = await api.device.async_get_bbox_summary()

                try:
                    sn = infos[0]["device"]["serialnumber"]
                    assert sn is not None, "Null Bbox serial number retrieved"
                except (IndexError, KeyError, AssertionError) as err:
                    raise CannotConnect("Serial number of device not found") from err

                await self.async_set_unique_id(sn)
                self._abort_if_unique_id_configured()

            except (HttpRequestError, CannotConnect) as err:
                _LOGGER.warning("Can not to connect at Bbox: %s", err)
                errors["base"] = "cannot_connect"
            except InvalidAuth as err:
                _LOGGER.warning("Fail to authenticate to the Bbox: %s", err)
                errors["base"] = "invalid_auth"
            except BboxException as err:
                _LOGGER.exception("Unknown error connecting to the Bbox: %s", err)
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title="Bouygues Bbox", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
