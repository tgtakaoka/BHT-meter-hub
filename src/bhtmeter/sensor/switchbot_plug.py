import time

from .ble_sensor import BLESensor


class SwitchbotPlug(BLESensor):
    _WOAN_TECH = 0x0969

    @staticmethod
    def create(name: str, config: dict) -> "SwitchbotPlug":
        return SwitchbotPlug(name, config)

    def __init__(self, name: str, config: dict):
        super().__init__(name, SwitchbotPlug._WOAN_TECH, config)
        data = config["data"]
        self._p = data.get("power", None)

    @property
    def power(self):
        return self.current_data.get("p", 0)

    def decode(self, payload: bytearray) -> None:
        epoch_milli = int(time.time() * 1000)
        state = bool(payload[7] & 0b10000000)
        delay = bool(payload[8] & 0b00000001)
        timer = bool(payload[8] & 0b00000010)
        sync = bool(payload[8] & 0b00000100)
        wifi = payload[9]
        overload = bool(payload[10] & 0b10000000)
        power = ((payload[10] & 0b01111111) * 256 + payload[11]) / 10.0
        self.current_data = {
            "milli": epoch_milli,
            "state": state,
            "delay": delay,
            "timer": timer,
            "sync": sync,
            "wifi": wifi,
            "overload": overload,
            "p": power,
        }

    def display(self) -> None:
        data = self.current_data
        if not data:
            return
        power = data["p"]
        print(f"{self.name:<8}: power:{power:4.1f} W")

    def gather_data(self, data: dict) -> None:
        if not self.current_data:
            return
        self._gather_data(data, self._p, self.power, self.sense_milli)
