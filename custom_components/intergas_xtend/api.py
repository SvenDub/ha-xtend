import logging
from enum import IntFlag, IntEnum
from typing import TypedDict, Any, Callable, NotRequired

import httpx
from tenacity import retry, stop_after_attempt, wait_random

_LOGGER = logging.getLogger(__name__)

class ServiceFlags(IntFlag):
    HEATPUMP_NOT_ALLOWED = 1
    HP_FAILED_BACKUP_ACTIVE = 2
    BOILER_NEEDED = 4
    HP_COP_EFFICIENCY_OKAY = 8
    INITIAL_DELAY_DONE = 16
    START_WITH_BOILER_IMMEDIATELY = 32
    BACKUP_REQ_PREV = 64
    HEATPUMP_REQUESTED = 128
    BOILER_REQUESTED = 256
    BOILER_ACTUAL_STATE = 512
    BOILER_OPEN_LOOP_CONTROL = 1024
    BOILER_FLAME_DETECTED = 2048
    BOILER_FLAME_DUR_SHORT = 4096
    LOW_LOAD_DETECTED = 8192
    DEFROST_ACTIVE = 16384
    BLOCK_HP_CLOCK_PROGRAM = 32768

class DeviceFlags(IntFlag):
    LOW_LOAD_ENABLE = 1
    CONTROL_SUPPLY_TEMPERATURE = 2
    PROGRESSIVE_TEMP_REQUEST = 4
    SILENT_MODE_ACTIVE = 8
    HEATPUMP_FORCE_MAX_POWER = 16
    HEATPUMP_REGULATE_MAX_POWER = 32
    HEAT_WAS_AT_MINIMUM_FREQ = 64
    COMPRESSOR_WAS_ON = 128

class DeviceStatus(IntEnum):
    SENSORTEST = 85
    COMMISSIONING = 86
    CRANKHEATING = 87
    COMMISSIONING_WAITING = 88
    SERVICE = 170
    HEATPUMP_SELFTEST = 171
    DHW = 204
    DHW_INT = 51
    BOILER_INT = 240
    BOILER_EXT = 15
    POSTRUN_BOILER = 153
    CH = 102
    CH_WAIT = 103
    DEFROSTING = 104
    DEFROSTING_WAIT = 105
    DEFROSTING_WAIT_FLOW = 106
    CH_BLOCKED_BY_SGREADY = 107
    CH_WAIT_DHW_ACTIVE = 108
    CH_CONCRETE_DRYING = 109
    OPENTHERM = 0
    HEATUP = 255
    FROST = 24
    STARTING_CH = 230
    POSTRUN_CH = 231
    STANDBY = 126
    SWITCHED_OFF = 127
    CH_RF = 37
    DHW_HRECO = 205
    DHW_LEGIONELLA_PREVENTION = 206
    DHW_WAIT = 207
    STARTING_COOLING = 117
    COOLING = 118
    COOLING_WAIT = 119
    COOLING_BLOCKED_BY_SGREADY = 120
    COOLING_WAITING_FOR_FLOW = 121
    COOLING_CONDENSE_PROTECTION = 122
    COOLING_FLOOR_THERMOSTAT_OFF = 123
    POSTRUN_COOLING = 189

class BlockReason(IntEnum):
    BIVALENT_HEATPUMP_BLOCKED_REASON_NONE = 0
    BIVALENT_HEATPUMP_BLOCKED_REASON_NO_DEMAND = 1
    BIVALENT_HEATPUMP_BLOCKED_REASON_LOCKOUT = 2
    BIVALENT_HEATPUMP_BLOCKED_REASON_HEATPUMP_FAULT = 3
    BIVALENT_HEATPUMP_BLOCKED_REASON_COLD_START_OVERRIDE = 4
    BIVALENT_HEATPUMP_BLOCKED_REASON_OVERTEMPERATURE = 5
    BIVALENT_HEATPUMP_BLOCKED_REASON_PASSIVE_DEFROST = 6
    BIVALENT_HEATPUMP_BLOCKED_REASON_ACTIVE_DEFROST_PROHIBITED = 7
    BIVALENT_HEATPUMP_BLOCKED_REASON_SENSOR_CAL = 8
    BIVALENT_HEATPUMP_BLOCKED_REASON_OUTSIDE_ODU_OPRANGE = 32
    BIVALENT_HEATPUMP_BLOCKED_REASON_HIGH_WATERTEMP = 33
    BIVALENT_HEATPUMP_BLOCKED_REASON_LOW_OUTDOORTEMP = 34
    BIVALENT_HEATPUMP_BLOCKED_REASON_SGREADY = 35
    BIVALENT_HEATPUMP_BLOCKED_REASON_BOILER_ONLY_OP = 36
    BIVALENT_HEATPUMP_BLOCKED_REASON_CLOCK_PROGRAM = 37
    BIVALENT_HEATPUMP_BLOCKED_REASON_COP_LOW = 38
    BIVALENT_HEATPUMP_BLOCKED_REASON_NO_TOD_SENSOR = 39
    BIVALENT_HEATPUMP_BLOCKED_REASON_LOW_WATERTEMP = 40
    BIVALENT_HEATPUMP_BLOCKED_REASON_HIGH_OUTDOORTEMP = 41
    BIVALENT_HEATPUMP_BLOCKED_REASON_DHW_BACKUP_ACTIVE = 42
    BIVALENT_HEATPUMP_BLOCKED_REASON_DM_CONTROL_STOP = 43
    BIVALENT_HEATPUMP_BLOCKED_REASON_EXTERNAL_POWER_LIMIT = 44
    BIVALENT_HEATPUMP_BLOCKED_REASON_COOLING_CONDENSE_PROT = 45
    BIVALENT_HEATPUMP_BLOCKED_REASON_COOLING_FLOOR_THERMOSTAT = 46
    BIVALENT_HEATPUMP_BLOCKED_REASON_UNKNOWN = 255

class SensorMapping(TypedDict):
    key: str
    mapper: NotRequired[Callable[[int | None], Any]]

SENSORS_MAP: dict[str, SensorMapping] = {
    "power_heat_pump": {"key": "503e"},
    "cop": {"key": "5041", "mapper": lambda v: v / 10},
    "power_total_thermal": {"key": "5077"},
    "power_boiler": {"key": "5088"},
    "power_electrical": {"key": "50f2"},
    "silent_mode": {"key": "77c3", "mapper": lambda v: DeviceFlags.SILENT_MODE_ACTIVE in DeviceFlags(v) if v is not None else None},
    "device_status": {"key": "7e51", "mapper": lambda v: DeviceStatus(v) if v is not None else None},
    "heat_demand_heat_pump": {"key": "f9f2", "mapper": lambda v: ServiceFlags.HEATPUMP_REQUESTED in ServiceFlags(v) if v is not None else None},
    "heat_demand_boiler": {"key": "f9f2", "mapper": lambda v: ServiceFlags.BOILER_REQUESTED in ServiceFlags(v) if v is not None else None},
    "compressor_frequency": {"key": "65a7", "mapper": lambda v: v / 100},
    "fan_speed": {"key": "6c8a"},
    "water_flow": {"key": "629c", "mapper": lambda v: v / 100},
    "water_setpoint": {"key": "62ed", "mapper": lambda v: v / 100},
    "water_supply": {"key": "621d", "mapper": lambda v: v / 100},
    "water_return": {"key": "6280", "mapper": lambda v: v / 100},
    "temperature_room": {"key": "79b3", "mapper": lambda v: v / 100},
    "temperature_setpoint_room": {"key": "7921", "mapper": lambda v: v / 100},
    "temperature_outdoor": {"key": "62d1", "mapper": lambda v: v / 100},
    "energy_electrical_total": {"key": "63b3"},
    "energy_thermal_total": {"key": "63f0"},
    "energy_electrical_yesterday": {"key": "5099", "mapper": lambda v: v / 10},
    "energy_thermal_yesterday": {"key": "50ae", "mapper": lambda v: v / 10},
    "cop_yesterday": {"key": "50f7", "mapper": lambda v: v / 10},
    "sw_version": {"key": "47e0"},
    "boiler_water_supply": {"key": "7ee6", "mapper": lambda v: v / 100},
    "boiler_water_return": {"key": "7e81", "mapper": lambda v: v / 100},
    "boiler_water_setpoint": {"key": "7e31", "mapper": lambda v: v / 100 if v < 32767 else None},
    "boiler_modulation_level": {"key": "84d1", "mapper": lambda v: v / 100},
    "boiler_oem_faultcode": {"key": "8439"},
    "block_reason": {"key": "7fec", "mapper": lambda v: BlockReason(v)},
}

class IntergasXtendStateData:
    def __init__(self, data: dict):
        self.data = data
        self.sensors = self.__map_sensors()
        
    def __map_sensors(self):
        return {
            key: value.get("mapper", lambda v: v)(self.data.get("stats", {}).get(value["key"], None))
            for key, value in SENSORS_MAP.items()
        }

class IntergasXtendAPI:
    def __init__(self, url: str, validate_https: bool):
        self.url = url
        self.validate_https = validate_https

    @retry(stop=stop_after_attempt(3), wait=wait_random(1, 2), reraise=True)
    async def get_device_info(self):
        async with self.create_client() as client:
            endpoint = self.url + "/api/stats/values?fields=47e0"
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_random(1, 2), reraise=True)
    async def get_state_data(self) -> IntergasXtendStateData:
        async with self.create_client() as client:
            endpoint = self.url + f"/api/stats/values?fields={",".join((value.get("key") for value in SENSORS_MAP.values()))}"
            response = await client.get(endpoint)
            response.raise_for_status()
            return IntergasXtendStateData(response.json())

    def create_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(verify=self.validate_https)
