"""Platform for binary sensor integration."""

import asyncio
from datetime import timedelta
from urllib.parse import urlparse

import aiohttp

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import (
    CONF_UPDATE_INTERVAL,
    CONF_VERIFY_SSL,
    DOMAIN,
    LOGGER,
    ATTR_LAST_STATUS,
    ATTR_LAST_ERROR_STATUS,
)


SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the WebCheck sensor from a config entry."""
    url = entry.data[CONF_URL]
    name = entry.data.get(CONF_NAME, urlparse(url).netloc)
    update_interval = entry.data.get(CONF_UPDATE_INTERVAL, 10)
    verify_ssl = entry.data.get(CONF_VERIFY_SSL, True)

    websession = async_create_clientsession(
        hass,
        timeout=aiohttp.ClientTimeout(
            # Use timeout of 9 to avoid "Update takes over 10 seconds" warning in HA logs
            total=9,
            connect=None,
            sock_connect=None,
            sock_read=None,
        ),
    )

    entity = WebCheckSensor(websession, url, name, update_interval, verify_ssl, entry.entry_id)
    LOGGER.debug(f"Added entity for url:{url}, name:{name}")
    async_add_entities([entity], True)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the sensor platform.
    
    This is kept for backwards compatibility but all setup should
    go through config entries now.
    """
    # We no longer support setup from YAML directly
    # All setup should go through config entries
    return


class WebCheckSensor(BinarySensorEntity):
    """Representation of a WebCheck sensor."""

    def __init__(self, websession, url, name, update_interval, verify_ssl, entry_id):
        """Initialize the sensor."""
        self._is_down = None
        self._url = url
        self._verify_ssl = verify_ssl
        self._websession = websession
        self._update_interval = update_interval
        self._update_interval_remaining = 0  # Make sure to update at startup
        self._last_status = "Not updated yet"
        self._last_error_status = "None"
        self._entry_id = entry_id
        
        # Set entity attributes
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{self._entry_id}"
        
        # Parse URL for device info
        url_parts = urlparse(self._url)
        self._hostname = url_parts.netloc

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=self._attr_name,
            manufacturer="WebCheck",
            model="Website Monitor",
            configuration_url=self._url,
        )

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._is_down

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._is_down is not None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return the state attributes."""
        return {
            "url": self._url,
            ATTR_LAST_STATUS: self._last_status,
            ATTR_LAST_ERROR_STATUS: self._last_error_status,
        }

    async def async_update(self):
        """Do a request to the website"""
        self._update_interval_remaining -= 1
        if self._update_interval_remaining <= 0:
            self._update_interval_remaining = self._update_interval
            try:
                LOGGER.debug("Start checking: %s", self._url)
                async with self._websession.get(
                    self._url, verify_ssl=self._verify_ssl
                ) as resp:
                    LOGGER.debug(
                        "Done checking: %s, status = %s", self._url, resp.status
                    )
                    self._is_down = resp.status >= 500
                    self._last_status = f"{resp.status} - {resp.reason}"
            except aiohttp.ClientSSLError:
                LOGGER.debug("ClientSSLError for %s", self._url)
                self._is_down = True
                self._last_status = "Client SSL error"
                self._last_error_status = self._last_status
            except aiohttp.ClientConnectionError:
                LOGGER.debug("ConnectionError for %s", self._url)
                self._is_down = True
                self._last_status = "Connection error"
                self._last_error_status = self._last_status
            except asyncio.TimeoutError:
                LOGGER.debug("Timeout for %s", self._url)
                self._is_down = True
                self._last_status = "Timeout"
                self._last_error_status = self._last_status
            except:
                LOGGER.exception("Unhandled exception for %s", self._url)
                self._is_down = True
                self._last_status = "Unhandled error"
                self._last_error_status = self._last_status
