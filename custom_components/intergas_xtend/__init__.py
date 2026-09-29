import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.intergas_xtend.coordinator import IntergasXtendCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

type IntergasXtendConfigEntry = ConfigEntry[IntergasXtendCoordinator]

async def async_setup_entry(hass: HomeAssistant, entry: IntergasXtendConfigEntry) -> bool:
    
    coordinator = IntergasXtendCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    entry.runtime_data = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True