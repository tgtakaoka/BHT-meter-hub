from bluepy import btle
import time

from . import Sensor

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self, sensors: list, args):
        super().__init__()
        self.data = {}
        self._args = args
        self._sensors = {}
        for sensor in sensors:
            if isinstance(sensor, BLESensor) and not sensor.disabled:
                self._sensors[sensor.macaddr] = sensor

    @property
    def sensors(self) -> dict:
        return self._sensors

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr in self._sensors.keys():
            sensor = self._sensors[dev.addr]
            scanData = dev.getScanData()
            for (adtype, desc, payload) in scanData:
                if adtype == sensor.addr_type:
                    if sensor.verbose:
                        sensor.sense_message()
                    sensor.decode(payload)
        elif self._args.verbose:
            print('.', end='', flush=True)

class BLESensor(Sensor):
    @staticmethod
    def scan_sensors(args):
        delegate = ScanDelegate(Sensor.sensors(), args)
        if args.verbose:
            for macaddr in delegate.sensors:
                sensor = delegate.sensors[macaddr]
                print('scan BLE {:s} {:s} ({:s})'.format(
                    macaddr, sensor.name, sensor.sensor_class))
        if not args.sense:
            return
        scanner = btle.Scanner().withDelegate(delegate)
        for i in range(5):
            try:
                scanner.scan(args.ble_timeout)
            except btle.BTLEException as e:
                if args.verbose:
                    print(f'ERROR: BTLE Exception: retry{i+1}')
                    print(f'ERROR:   type: {type(e)}')
                    print(f'ERRPR:   args: {e.args}')
                time.sleep(5)
            else:
                break
        if args.verbose:
            print()

    def __init__(self, name: str, addr_type: int, config: dict):
        super().__init__(name, config)
        ble = config.get('ble', None)
        if type(ble) != dict:
            raise ValueError('sensor.{:s} must have ble table'.format(name))
        macaddr = ble.get('macaddr', ble)
        if type(macaddr) != str:
            raise ValueError('sensor.{:s}.ble must have macaddr'.format(name))
        self._macaddr = macaddr.lower()
        self._addr_type = addr_type

    @property
    def macaddr(self) ->str:
        return self._macaddr
    @property
    def addr_type(self) -> int:
        return self._addr_type

    def decode(self, payload: str) -> None:
        pass
