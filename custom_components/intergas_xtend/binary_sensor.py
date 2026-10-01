from homeassistant.components.binary_sensor import BinarySensorEntityDescription, BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntergasXtendConfigEntry, IntergasXtendCoordinator
from .const import DOMAIN, DEFAULT_NAME

SENSOR_DESCRIPTIONS = [
    BinarySensorEntityDescription(
        key="heat_demand_heat_pump",
        name="Heat Demand (Heat Pump)",
        icon="mdi:radiator",
    ),
    BinarySensorEntityDescription(
        key="heat_demand_boiler",
        name="Heat Demand (Boiler)",
        icon="mdi:radiator",
    ),
    BinarySensorEntityDescription(
        key="silent_mode",
        name="Silent Mode",
        icon="mdi:volume-off",
    )
]

async def async_setup_entry(hass: HomeAssistant, config_entry: IntergasXtendConfigEntry, add_entities: AddEntitiesCallback):
    coordinator = config_entry.runtime_data

    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(IntergasXtendBinarySensor(coordinator, description))

    add_entities(entities)

class IntergasXtendBinarySensor(CoordinatorEntity[IntergasXtendCoordinator], BinarySensorEntity):
    def __init__(self, coordinator: IntergasXtendCoordinator, description: BinarySensorEntityDescription):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(coordinator.config_entry.unique_id))},
            name=DEFAULT_NAME,
            manufacturer="Intergas",
            model="Xtend",
            sw_version=coordinator.data.sensors.get("sw_version"),
        )

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.sensors.get(self.entity_description.key)
