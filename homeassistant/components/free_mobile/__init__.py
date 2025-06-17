"""The Free Mobile integration."""

from __future__ import annotations

from dataclasses import dataclass

from freesms import FreeClient

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PLATFORM,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

#DATA_HASS_CONFIG
from .const import DOMAIN

_PLATFORMS: list[Platform] = [Platform.NOTIFY]

type FreeMobileConfigEntry = ConfigEntry[FreeMobileData]

@dataclass
class FreeMobileData:
    """Free Mobile data type."""

    client: FreeClient

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Slack component."""
    #hass.data[DATA_HASS_CONFIG] = config

    # Iterate all entries for notify to only get Slack
    if Platform.NOTIFY in config:
        for entry in config[Platform.NOTIFY]:
            if entry[CONF_PLATFORM] == DOMAIN:
                hass.async_create_task(
                    hass.config_entries.flow.async_init(
                        DOMAIN, context={"source": SOURCE_IMPORT}, data=entry
                    )
                )

    return True

async def async_setup_entry(hass: HomeAssistant, entry: FreeMobileConfigEntry) -> bool:
    """Set up Free Mobile from a config entry."""

    free_client = FreeClient(entry.data[CONF_USERNAME], entry.data[CONF_ACCESS_TOKEN])
    entry.runtime_data = FreeMobileData(free_client)

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: FreeMobileConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
