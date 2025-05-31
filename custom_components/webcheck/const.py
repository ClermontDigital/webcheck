"""Constants for the WebCheck integration."""

import logging

LOGGER = logging.getLogger(__package__)

DOMAIN = "webcheck"

CONF_WEBSITES = "websites"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_VERIFY_SSL = "verify_ssl"

# Device attributes
ATTR_LAST_STATUS = "last_status"
ATTR_LAST_ERROR_STATUS = "last_error_status"
