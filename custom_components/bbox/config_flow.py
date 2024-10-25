"""Config flow for Bouygues Bbox integration."""

from __future__ import annotations

from collections.abc import Mapping
import logging
from typing import Any

from bboxpy import Bbox
from bboxpy.exceptions import BboxException, HttpRequestError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_DEFAULTS,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_REFRESH_RATE,
    CONF_USE_TLS,
    DEFAULT_TITLE,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)


class BaseConfigFlow:

    async def async_check_user_input(self, user_input: Mapping[str, Any] | None) -> str | None:
        """
        Check Bbox connection with user input
        Return Bbox serial number on success and set self._errors
        otherwise.
        """
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
                serialnumber = infos[0]["device"]["serialnumber"]
                assert serialnumber is not None, "Null Bbox serial number retrieved"
                return serialnumber
            except (IndexError, KeyError, AssertionError):
                self._errors["base"] = "serialnumber"

        except (HttpRequestError, CannotConnect) as err:
            _LOGGER.warning("Can not to connect at Bbox: %s", err)
            self._errors["base"] = "cannot_connect"
        except InvalidAuth as err:
            _LOGGER.warning("Fail to authenticate to the Bbox: %s", err)
            self._errors["base"] = "invalid_auth"
        except BboxException as err:
            _LOGGER.exception("Unknown error connecting to the Bbox: %s", err)
            self._errors["base"] = "unknown"
        return False


    @staticmethod
    def _get_config_schema(defaults=None, password_optional=False):
        """Get configuration schema"""
        defaults = defaults or CONF_DEFAULTS
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=defaults.get(CONF_HOST)): str,
                (
                    vol.Optional(CONF_PASSWORD) if password_optional
                    else vol.Required(CONF_PASSWORD)
                ): str,
                vol.Required(CONF_USE_TLS, default=defaults.get(CONF_USE_TLS)): bool,
                vol.Required(CONF_REFRESH_RATE, default=defaults.get(CONF_REFRESH_RATE)): int,
            }
        )


class ConfigFlow(BaseConfigFlow, config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bouygues Bbox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        self._errors: dict[str, str] = {}
        if user_input:
            serialnumber = await self.async_check_user_input(user_input)
            if serialnumber and not self._errors:
                await self.async_set_unique_id(serialnumber)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=DEFAULT_TITLE, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self._get_config_schema(),
            errors=self._errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow(config_entry)


class OptionsFlow(BaseConfigFlow, config_entries.OptionsFlow):
    """Handle a options flow for Bouygues Bbox."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        self._errors: dict[str, str] = {}
        if user_input:
            if not user_input.get(CONF_PASSWORD):
                _LOGGER.debug("User do not enter password, keep current configured one")
                user_input[CONF_PASSWORD] = self.config_entry.data[CONF_PASSWORD]
            serialnumber = await self.async_check_user_input(user_input)
            if serialnumber and not self._errors:
                # update config entry
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=user_input
                )
                # Finish
                return self.async_create_entry(data=None)

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_config_schema(
                self.config_entry.data,
                password_optional=self.config_entry.data.get(CONF_PASSWORD)
            ),
            errors=self._errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
