"""Support for Free Mobile SMS platform."""

from __future__ import annotations

from http import HTTPStatus
import logging
import voluptuous as vol

from urllib3.request import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError

from homeassistant.components.notify import (
    PLATFORM_SCHEMA as NOTIFY_PLATFORM_SCHEMA,
    BaseNotificationService,
)
from homeassistant.const import CONF_ACCESS_TOKEN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = NOTIFY_PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_USERNAME): cv.string, vol.Required(CONF_ACCESS_TOKEN): cv.string}
)

class configFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Example config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1
    
    async def async_step_user(self, info):
        if info is not None:
            await self.async_set_unique_id(info)
            pass  # TODO: process info

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("password"): str})
        )
    async def async_step_token(self, info):
        if info is not None:
            pass  # TODO: process info

        return self.async_show_form(
            step_id="token", data_schema=vol.Schema({vol.Required("password"): str})
        )

def get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> FreeSMSNotificationService:
    """Get the Free Mobile SMS notification service."""
    return FreeSMSNotificationService(config[CONF_USERNAME], config[CONF_ACCESS_TOKEN])


class FreeSMSNotificationService(BaseNotificationService):
    """Implement a notification service for the Free Mobile SMS service."""

    def __init__(self, username, access_token):
        """Initialize the service."""
        #self.free_client = FreeClient(username, access_token)

    def send_message(self, message="", **kwargs):
        """Send a message to the Free Mobile user cell."""
        resp = urlopen("https://smsapi.free-mobile.fr/sendmsg?{}".format(urlencode({"user": config[CONF_USERNAME], "pass": config[CONF_ACCESS_TOKEN], "msg": message})))

        if resp.status_code == HTTPStatus.BAD_REQUEST:
            _LOGGER.error("At least one parameter is missing")
        elif resp.status_code == HTTPStatus.PAYMENT_REQUIRED:
            _LOGGER.error("Too much SMS send in a few time")
        elif resp.status_code == HTTPStatus.FORBIDDEN:
            _LOGGER.error("Wrong Username/Password")
        elif resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR:
            _LOGGER.error("Server error, try later")
