from collections.abc import Callable

from homeassistant.components.climate import HVACMode, HVACAction
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass, SensorEntity, SensorDeviceClass
from homeassistant.const import UnitOfPower, UnitOfFrequency, UnitOfVolumeFlowRate, UnitOfTemperature, UnitOfEnergy, \
    EntityCategory, UnitOfRatio
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import IntergasXtendConfigEntry
from .api import DeviceStatus
from .const import DOMAIN, DEFAULT_NAME
from .coordinator import IntergasXtendCoordinator


class IntergasXtendSensorEntityDescription(SensorEntityDescription, frozen_or_thawed=True):
    value_fn: Callable[[IntergasXtendCoordinator], StateType] | None = None


def _compute_hvac_mode(coordinator: IntergasXtendCoordinator) -> str | None:
    if coordinator.data.sensors.get("heat_demand_heat_pump") or coordinator.data.sensors.get("heat_demand_boiler"):
        return HVACMode.HEAT
    return HVACMode.OFF


def _compute_hvac_action(coordinator: IntergasXtendCoordinator) -> str | None:
    device_status = coordinator.data.sensors.get("device_status")
    if device_status in (DeviceStatus.CH, DeviceStatus.STARTING_CH):
        return HVACAction.HEATING
    if device_status == DeviceStatus.DEFROSTING:
        return HVACAction.DEFROSTING
    if device_status in (DeviceStatus.HEATUP, DeviceStatus.CRANKHEATING):
        return HVACAction.PREHEATING
    if device_status == DeviceStatus.SWITCHED_OFF:
        return HVACAction.OFF
    if device_status == DeviceStatus.STANDBY:
        return HVACAction.IDLE
    return None


def _compute_device_status(coordinator: IntergasXtendCoordinator) -> str | None:
    device_status = coordinator.data.sensors.get("device_status")
    return device_status.name if device_status else None


SENSOR_DESCRIPTIONS: list[IntergasXtendSensorEntityDescription] = [
    IntergasXtendSensorEntityDescription(
        key="hvac_mode",
        translation_key="hvac_mode",
        name="HVAC Mode",
        icon="mdi:thermostat",
        device_class=SensorDeviceClass.ENUM,
        options=[
            HVACMode.OFF,
            HVACMode.HEAT,
        ],
        value_fn=_compute_hvac_mode,
    ),
    IntergasXtendSensorEntityDescription(
        key="hvac_action",
        translation_key="hvac_action",
        name="HVAC Action",
        icon="mdi:hvac",
        device_class=SensorDeviceClass.ENUM,
        options=[
            HVACAction.OFF,
            HVACAction.IDLE,
            HVACAction.PREHEATING,
            HVACAction.HEATING,
            HVACAction.DEFROSTING,
        ],
        value_fn=_compute_hvac_action,
    ),
    IntergasXtendSensorEntityDescription(
        key="power_heat_pump",
        name="Power (Heat Pump)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    IntergasXtendSensorEntityDescription(
        key="power_boiler",
        name="Power (Boiler)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    IntergasXtendSensorEntityDescription(
        key="power_total_thermal",
        name="Power (Total Thermal)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    IntergasXtendSensorEntityDescription(
        key="cop",
        name="COP",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
    ),
    IntergasXtendSensorEntityDescription(
        key="power_electrical",
        name="Power (Electrical)",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
    ),
    IntergasXtendSensorEntityDescription(
        key="device_status",
        translation_key="device_status",
        name="Device Status",
        icon="mdi:heat-pump",
        value_fn=_compute_device_status,
    ),
    IntergasXtendSensorEntityDescription(
        key="compressor_frequency",
        name="Compressor Frequency",
        native_unit_of_measurement=UnitOfFrequency.HERTZ,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.FREQUENCY,
    ),
    IntergasXtendSensorEntityDescription(
        key="fan_speed",
        name="Fan Speed",
        native_unit_of_measurement="rpm",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:fan",
    ),
    IntergasXtendSensorEntityDescription(
        key="water_flow",
        name="Water Flow",
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        suggested_display_precision=2,
    ),
    IntergasXtendSensorEntityDescription(
        key="water_return",
        name="Water Return",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="water_supply",
        name="Water Supply",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="water_setpoint",
        name="Water Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="temperature_outdoor",
        name="Outdoor Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="temperature_room",
        name="Room Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="temperature_setpoint_room",
        name="Room Temperature Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="energy_electrical_total",
        name="Total Heat Pump Energy (Electrical)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=0,
    ),
    IntergasXtendSensorEntityDescription(
        key="energy_thermal_total",
        name="Total Heat Pump Energy (Thermal)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=0,
    ),
    IntergasXtendSensorEntityDescription(
        key="energy_electrical_yesterday",
        name="Yesterday Heat Pump Energy (Electrical)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    IntergasXtendSensorEntityDescription(
        key="energy_thermal_yesterday",
        name="Yesterday Heat Pump Energy (Thermal)",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        suggested_display_precision=1,
    ),
    IntergasXtendSensorEntityDescription(
        key="sw_version",
        name="Firmware Version",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    IntergasXtendSensorEntityDescription(
        key="boiler_water_return",
        name="Boiler Water Return",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="boiler_water_supply",
        name="Boiler Water Supply",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="boiler_water_setpoint",
        name="Boiler Water Setpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    IntergasXtendSensorEntityDescription(
        key="boiler_modulation_level",
        name="Boiler Modulation Level",
        native_unit_of_measurement=UnitOfRatio.PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:percent",
    ),
    IntergasXtendSensorEntityDescription(
        key="boiler_oem_faultcode",
        name="Boiler OEM Faultcode",
        entity_category=EntityCategory.DIAGNOSTIC,
        icon="mdi:water-boiler-alert",
    ),
]


async def async_setup_entry(hass: HomeAssistant, config_entry: IntergasXtendConfigEntry,
                            add_entities: AddEntitiesCallback):
    coordinator = config_entry.runtime_data

    entities = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(IntergasXtendSensor(coordinator, description))

    add_entities(entities)


class IntergasXtendSensor(CoordinatorEntity[IntergasXtendCoordinator], SensorEntity):
    entity_description: IntergasXtendSensorEntityDescription

    def __init__(self, coordinator: IntergasXtendCoordinator,
                 description: IntergasXtendSensorEntityDescription) -> None:
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
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator)
        return self.coordinator.data.sensors.get(self.entity_description.key)
