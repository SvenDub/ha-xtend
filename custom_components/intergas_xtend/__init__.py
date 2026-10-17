import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.intergas_xtend.coordinator import IntergasXtendCoordinator, IntergasXtendStatisticsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]


@dataclass
class IntergasXtendConfigData:
    data_coordinator: IntergasXtendCoordinator
    statistics_coordinator: IntergasXtendStatisticsCoordinator


type IntergasXtendConfigEntry = ConfigEntry[IntergasXtendConfigData]


async def async_setup_entry(hass: HomeAssistant, entry: IntergasXtendConfigEntry) -> bool:
    data_coordinator = IntergasXtendCoordinator(hass, entry)
    await data_coordinator.async_config_entry_first_refresh()

    statistics_coordinator = IntergasXtendStatisticsCoordinator(hass, entry)
    await statistics_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = IntergasXtendConfigData(data_coordinator, statistics_coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
