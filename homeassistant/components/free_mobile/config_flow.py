"""Config flow for the Free Mobile integration."""

from __future__ import annotations

from http import HTTPStatus
import logging
from typing import Any

from freesms import FreeClient
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_ACCESS_TOKEN): str,
    }
)

def send_test_message(user, token):
    """Send a test message to validate the Free Mobile credentials."""
    free_client = FreeClient(user, token)

    try:
        resp = free_client.send_sms("Test message from Home Assistant")

        if resp.error():
            if resp.status_code == HTTPStatus.FORBIDDEN:
                raise InvalidAuth
            raise CannotConnect
    except (ConnectionError, TimeoutError) as ex:
        raise CannotConnect from ex

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    await hass.async_add_executor_job(send_test_message, data[CONF_USERNAME], data[CONF_ACCESS_TOKEN])


async def async_step_import(self, import_config: dict[str, str]) -> ConfigFlowResult:
    """Import a config entry from configuration.yaml."""
    _LOGGER.warning(
        "Configuration of the Free Mobile integration in YAML is deprecated and "
        "will be removed in a future release; Your existing configuration "
        "has been imported into the UI automatically and can be safely removed "
        "from your configuration.yaml file"
    )
    entries = self._async_current_entries()
    if any(x.data[CONF_USERNAME] == import_config[CONF_USERNAME] for x in entries):
        return self.async_abort(reason="already_configured")
    return await self.async_step_user(import_config)

class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Free Mobile."""

    VERSION = 1

    async def _show_setup_form(self, errors: dict[str, str] | None = None) -> ConfigFlowResult:
        """Show the setup form to the user."""
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors or {},
    )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return await self._show_setup_form(user_input)

        errors: dict[str, str] = {}
        try:
            await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
            return await self._show_setup_form(errors)
        except InvalidAuth:
            errors["base"] = "invalid_auth"
            return await self._show_setup_form(errors)
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
            return await self._show_setup_form(errors)
        else:
            if not self.unique_id:
                await self.async_set_unique_id(user_input.get(CONF_USERNAME))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input.get(CONF_USERNAME),
                data=user_input)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
