"""Config flow for Bouygues Bbox integration."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from bboxpy import AuthorizationError, Bbox, BboxException, HttpRequestError
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_VERIFY_SSL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import (
    CONF_REFRESH_RATE,
    CONF_USE_TLS,
    DEFAULT_HOST,
    DEFAULT_REFRESH_RATE,
    DEFAULT_TITLE,
    DEFAULT_USE_TLS,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_USE_TLS, default=DEFAULT_USE_TLS): bool,
        vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bouygues Bbox."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlow()

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
                    verify_ssl=user_input[CONF_VERIFY_SSL],
                )
                await api.async_login()
                infos = await api.device.async_get_bbox_summary()
                if (
                    isinstance(infos, list)
                    and len(infos) > 0
                    and (sn := infos[0].get("device", {}).get("serialnumber"))
                ):
                    await self.async_set_unique_id(sn)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title=DEFAULT_TITLE, data=user_input)

                errors["base"] = "serialnumber"

            except HttpRequestError as err:
                _LOGGER.warning("Can not to connect at Bbox: %s", err)
                errors["base"] = "cannot_connect"
            except AuthorizationError as err:
                _LOGGER.warning("Fail to authenticate to the Bbox: %s", err)
                errors["base"] = "invalid_auth"
            except BboxException:
                _LOGGER.exception("Unknown error connecting to the Bbox")
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Perform reauthentication upon an API authentication error."""
        self.entry_data = entry_data
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Confirm reauthentication dialog."""
        errors: dict[str, str] = {}
        if user_input:
            try:
                api = Bbox(
                    hostname=self.entry_data[CONF_HOST],
                    password=user_input[CONF_PASSWORD],
                    session=async_create_clientsession(self.hass),
                    use_tls=self.entry_data[CONF_USE_TLS],
                    verify_ssl=self.entry_data[CONF_VERIFY_SSL],
                )
                await api.async_login()
            except BboxException:
                errors["base"] = "cannot_connect"
            else:
                infos = await api.device.async_get_bbox_summary()
                if (
                    isinstance(infos, list)
                    and len(infos) > 0
                    and (sn := infos[0].get("device", {}).get("serialnumber"))
                ):
                    await self.async_set_unique_id(sn)
                    self._abort_if_unique_id_mismatch(reason="wrong_account")
                    return self.async_update_reload_and_abort(
                        self._get_reauth_entry(),
                        data_updates={CONF_PASSWORD: user_input[CONF_PASSWORD]},
                    )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )


class OptionsFlow(config_entries.OptionsFlow):
    """Handle a options flow for Bouygues Bbox."""

    async def async_step_init(
        self, user_input: Mapping[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {vol.Optional(CONF_REFRESH_RATE, default=DEFAULT_REFRESH_RATE): int}
                ),
                self.config_entry.options,
            ),
        )
