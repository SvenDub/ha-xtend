from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass, SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfPower, UnitOfFrequency, UnitOfVolumeFlowRate, UnitOfTemperature, UnitOfEnergy, \
    EntityCategory
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
        icon="mdi:percent",
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
        translation_key="device_status",
        name="Device Status",
        icon="mdi:heat-pump",
    ),
    SensorEntityDescription(
        key="compressor_frequency",
        name="Compressor Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
    ),
    SensorEntityDescription(
        key="fan_speed",
        name="Fan Speed",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    SensorEntityDescription(
        key="water_flow",
        name="Water Flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="water_return",
        name="Water Return",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="water_supply",
        name="Water Supply",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="water_setpoint",
        name="Water Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="temperature_outdoor",
        name="Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="temperature_room",
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="temperature_setpoint_room",
        name="Room Temperature Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    SensorEntityDescription(
        key="energy_electrical_total",
        name="Total Heat Pump Energy (Electrical)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="energy_thermal_total",
        name="Total Heat Pump Energy (Thermal)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="energy_electrical_yesterday",
        name="Yesterday Heat Pump Energy (Electrical)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="energy_thermal_yesterday",
        name="Yesterday Heat Pump Energy (Thermal)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="sw_version",
        name="Firmware Version",
        entity_category=EntityCategory.DIAGNOSTIC,
    )
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
            sw_version=coordinator.data.sensors.get("sw_version"),
        )

    @property
    def native_value(self) -> StateType:
        return self.coordinator.data.sensors.get(self.entity_description.key)