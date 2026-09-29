import httpx

SENSORS_MAP = {
    "503e": "power_heat_pump",
    "5041": "cop",
    "5077": "power_total_thermal",
    "5088": "power_boiler",
    "50f2": "power_electrical",
}

class IntergasXtendStateData:
    def __init__(self, data: dict):
        self.data = data
        self.sensors = self.__map_sensors()
        
    def __map_sensors(self):
        return {SENSORS_MAP.get(key, key): value for key, value in self.data.get("stats", {}).items()}

class IntergasXtendAPI:
    def __init__(self, url: str, validate_https: bool):
        self.url = url
        self.validate_https = validate_https

    async def get_device_info(self):
        async with httpx.AsyncClient(verify=self.validate_https) as client:
            response = await client.get(self.url + "/api/stats/values?fields=47e0")
            response.raise_for_status()
            return response.json()

    async def get_state_data(self) -> IntergasXtendStateData:
        async with httpx.AsyncClient(verify=self.validate_https) as client:
            response = await client.get(self.url + f"/api/stats/values?fields={",".join(SENSORS_MAP.keys())}")
            response.raise_for_status()
            return IntergasXtendStateData(response.json())
