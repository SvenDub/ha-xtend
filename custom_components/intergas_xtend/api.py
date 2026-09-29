import logging
from enum import IntFlag, IntEnum
from typing import TypedDict, Any, Callable, NotRequired

import httpx

_LOGGER = logging.getLogger(__name__)

class DeviceFlags(IntFlag):
    SILENT_MODE = 8

class DeviceStatus(IntEnum):
    SENSORTEST = 58
    CH = 102
    STANDBY = 126
    OFF = 127
    STARTING_CH = 230
    POSTRUN_CH = 231

class SensorMapping(TypedDict):
    key: str
    mapper: NotRequired[Callable[[int | None], Any]]

SENSORS_MAP: dict[str, SensorMapping] = {
    "power_heat_pump": {"key": "503e"},
    "cop": {"key": "5041"},
    "power_total_thermal": {"key": "5077"},
    "power_boiler": {"key": "5088"},
    "power_electrical": {"key": "50f2"},
    "silent_mode": {"key": "77c3", "mapper": lambda v: DeviceFlags.SILENT_MODE in DeviceFlags(v) if v is not None else None},
    "device_status": {"key": "7e51", "mapper": lambda v: DeviceStatus(v).name.lower() if v is not None else None},
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

    async def get_device_info(self):
        async with httpx.AsyncClient(verify=self.validate_https) as client:
            endpoint = self.url + "/api/stats/values?fields=47e0"
            response = await client.get(endpoint)
            response.raise_for_status()
            return response.json()

    async def get_state_data(self) -> IntergasXtendStateData:
        async with httpx.AsyncClient(verify=self.validate_https) as client:
            endpoint = self.url + f"/api/stats/values?fields={",".join((value.get("key") for value in SENSORS_MAP.values()))}"
            response = await client.get(endpoint)
            response.raise_for_status()
            return IntergasXtendStateData(response.json())
