from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass, SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntergasXtendConfigEntry
from .const import DOMAIN, DEFAULT_NAME
from .coordinator import IntergasXtendCoordinator

SENSOR_DESCRIPTIONS = [
    SensorEntityDescription(
        key="power_heat_pump",
        name="Power (Heat Pump)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="power_boiler",
        name="Power (Boiler)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="power_total_thermal",
        name="Power (Total Thermal)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="cop",
        name="COP",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="power_electrical",
        name="Power (Electrical)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    SensorEntityDescription(
        key="device_status",
        name="Device Status",
    ),
]

async def async_setup_entry(hass: HomeAssistant, config_entry: IntergasXtendConfigEntry, add_entities: AddEntitiesCallback):
    coordinator = config_entry.runtime_data
    
    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(IntergasXtendSensor(coordinator, description))
    
    add_entities(entities)
    
class IntergasXtendSensor(CoordinatorEntity[IntergasXtendCoordinator], SensorEntity):
    def __init__(self, coordinator: IntergasXtendCoordinator, description: SensorEntityDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(coordinator.config_entry.unique_id))},
            name=DEFAULT_NAME,
            manufacturer="Intergas",
            model="Xtend",
        )

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.sensors.get(self.entity_description.key)