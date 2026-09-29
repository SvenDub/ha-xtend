import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IntergasXtendAPI, IntergasXtendStateData
from .const import CONF_URL, DOMAIN, CONF_VALIDATE_CERT

_LOGGER = logging.getLogger(__name__)

class IntergasXtendCoordinator(DataUpdateCoordinator[IntergasXtendStateData]):
    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
            always_update=False,
        )
        self.api = IntergasXtendAPI(config_entry.data[CONF_URL], config_entry.data[CONF_VALIDATE_CERT])
        
    async def _async_update_data(self):
        try:
            return await self.api.get_state_data()
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
