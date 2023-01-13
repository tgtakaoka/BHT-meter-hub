import time

from .ble_sensor import BLESensor


class SwitchbotTH(BLESensor):
    _WOAN_TECH = 0x969

    @staticmethod
    def create(name: str, config: dict) -> "SwitchbotTH":
        return SwitchbotTH(name, config)

    def __init__(self, name: str, config: dict):
        super().__init__(name, SwitchbotTH._WOAN_TECH, config)
        data = config["data"]
        self._t = data.get("temperature", None)
        self._h = data.get("humidity", None)

    @property
    def temperature(self):
        return self.current_data.get("t", 0)

    @property
    def temperature_unit(self) -> str:
        return self.current_data.get("tu", "C")

    @property
    def celsius(self):
        if self.temperature_unit == "C":
            return self.temperature
        fahrenheit = self.temperature
        return (fahrenheit - 32) / 1.8

    @property
    def fahrenheit(self):
        if self.temperature_unit == "F":
            return self.temperature
        celsius = self.temperature
        return (celsius * 1.8) + 32

    @property
    def humidity(self):
        return self.current_data.get("h", 0)

    def decode(self, payload: bytearray) -> None:
        epoch_milli = int(time.time() * 1000)
        temp = (payload[8] & 0b00001111) / 10.0 + (payload[9] & 0b01111111)
        isTempPositive = bool(payload[9] & 0b10000000)
        if not isTempPositive:
            temp = -temp
        tunit = "F" if bool(payload[10] & 0b1000_0000) else "C"
        humid = payload[10] & 0b01111111
        self.current_data = {
            "milli": epoch_milli,
            "t": temp,
            "tu": tunit,
            "h": humid,
        }

    def display(self) -> None:
        data = self.current_data
        if not data:
            return
        temp = data["t"]
        tunit = data["tu"]
        humid = data["h"]
        print(f"{self.name:<8}: {temp:4.1f} {tunit} {humid:3} RH%")

    def gather_data(self, data: dict) -> None:
        if not self.current_data:
            return
        self._gather_data(data, self._t, self.celsius, self.sense_milli)
        self._gather_data(data, self._h, self.humidity, self.sense_milli)
