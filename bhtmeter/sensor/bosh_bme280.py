import time
from bme280 import BME280
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

from . import Sensor

class BoshBME280(Sensor):
    @staticmethod
    def create(name: str, config: dict) -> 'BoshBME280':
        i2c = config.get('i2c', None)
        if type(i2c) != dict:
            raise ValueError('sensor.{:s} must have i2c table'.format(name))
        i2c_bus = i2c.get('bus', i2c)
        if type(i2c_bus) != int:
            raise ValueError('sensor.{:s}.i2c must have bus number'.format(name))
        i2c_addr = i2c.get('address', None)
        if type(i2c_addr) != int:
            raise ValueError('sensor.{:s}.i2c must have address'.format(name))
        return BoshBME280(name, i2c_bus, i2c_addr, config)

    def __init__(self, name: str, bus: int, addr: int, config: dict):
        super().__init__(name, config)
        self._bus = bus
        self._addr = addr
        self._sensor = None
        data = config['data']
        self._p = data.get('pressure', None)
        self._t = data.get('temperature', None)
        self._h = data.get('humidity', None)

    @property
    def pressure(self):
        return self.current_data.get('p', 0)
    @property
    def temperature(self):
        return self.current_data.get('t', 0)
    @property
    def humidity(self):
        return self.current_data.get('h', 0)

    def _ensure_sensor(self):
        if not self._sensor:
            self._sensor = BME280(i2c_dev=SMBus(self._bus), i2c_addr=self._addr)
            self._sensor.setup(mode='forced')

    def sense_data(self) -> None:
        self.sense_message()
        if not self.do_sense:
            return
        try:
            self._ensure_sensor()
        except PermissionError as e:
            print('permission error {:s}; skip {:s} sensor'.format(str(e), self.name))
            return
        epoch_milli = int(time.time() * 1000)
        temp = self._sensor.get_temperature()
        pressure = self._sensor.get_pressure()
        humid = self._sensor.get_humidity()
        self.current_data = { 'milli': epoch_milli, 'p': pressure, 't': temp, 'h': humid }

    def disaplay(self) -> None:
        print(f'    Created:   {self.sense_milli}')
        print(f'Temperature:   {self.temperature:4.1f} C')
        print(f'   Humidity:   {self.humidity:4.1f} RH%')
        print(f'   Pressure: {self.pressure:6.1f} hPa')

    def gather_data(self, data: dict) -> None:
        self._gather_data(data, self._p, self.pressure, self.sense_milli)
        self._gather_data(data, self._t, self.temperature, self.sense_milli)
        self._gather_data(data, self._h, self.humidity, self.sense_milli)
