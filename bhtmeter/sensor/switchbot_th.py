import binascii
import time
from .ble_sensor import BLESensor

class SwitchbotTH(BLESensor):
    @staticmethod
    def create(name: str, config: dict) -> 'SwitchbotTH':
       return SwitchbotTH(name, config)

    def __init__(self, name: str, config: dict):
        super().__init__(name, 22, config)
        data = config['data']
        self._t = data.get('temperature', None)
        self._h = data.get('humidity', None)
        self._b = data.get('battery', None)

    @property
    def temperature(self):
        return self.current_data.get('t', 0)
    @property
    def humidity(self):
        return self.current_data.get('h', 0)
    @property
    def battery(self):
        return self.current_data.get('b', 0)

    def decode(self, payload: str) -> None:
        epoch_milli = int(time.time() * 1000)
        data = binascii.unhexlify(payload[8:])
        batt = data[0] & 0b01111111
        temp = (data[1] & 0b00001111) / 10.0 + (data[2] & 0b01111111)
        isTempPositive = bool(data[2] & 0b10000000)
        if not isTempPositive:
            temp = -temp
        humid = data[3] & 0b01111111
        self.current_data = { 'milli': epoch_milli, 't': temp, 'h': humid, 'b': batt }

    def display(self) -> None:
        data = self.current_data
        if not data:
            return
        temp = data['t']
        humid = data['h']
        batt = data['b']
        print(f'{self.name:<8}: {temp:4.1f} C {humid:3} RH%  {batt:3} BT%')

    def gather_data(self, data: dict) -> None:
        if not self.current_data:
            return
        self._gather_data(data, self._t, self.temperature, self.sense_milli)
        self._gather_data(data, self._h, self.humidity, self.sense_milli)
        self._gather_data(data, self._b, self.battery, self.sense_milli)
