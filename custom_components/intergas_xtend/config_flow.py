import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import IntergasXtendAPI
from .const import DOMAIN, CONF_URL, CONF_VALIDATE_CERT, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_URL): str,
    vol.Required(CONF_VALIDATE_CERT, default=True): bool,
})

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    api = IntergasXtendAPI(data[CONF_URL], data[CONF_VALIDATE_CERT])
    
    try:
        await api.get_device_info()
    except Exception:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect
    else:
        return {"title": DEFAULT_NAME}

class IntergasXtendConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )
        
        errors = {}
        
        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)
            
        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

class CannotConnect(HomeAssistantError):
    pass