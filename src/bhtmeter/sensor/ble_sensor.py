import asyncio
import time

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from . import Sensor


class BLESensor(Sensor):
    _BLE_SENSORS = {}
    _ARGS = None
    _SCANNING = {}
    _DOTS = 0

    @staticmethod
    def clear_dots():
        if BLESensor._DOTS > 0:
            print()
            BLESensor._DOTS = 0

    @staticmethod
    def print_dot():
        print(".", end="", flush=True)
        BLESensor._DOTS += 1

    @staticmethod
    def scan_sensors(args):
        BLESensor._ARGS = args
        BLESensor._SCANNING = {}
        for macaddr, sensor in BLESensor._BLE_SENSORS.items():
            BLESensor._SCANNING[macaddr] = sensor
            if args.verbose:
                print(
                    "scan BLE {:s} {:s} ({:s})".format(macaddr, sensor.name, sensor.sensor_class)
                )
        BLESensor.clear_dots()
        asyncio.run(BLESensor._scan_devices())
        if args.verbose:
            print()

    @staticmethod
    def _device_found(device: BLEDevice, adv_data: AdvertisementData) -> None:
        sensor = BLESensor._SCANNING.get(device.address, None)
        if sensor:
            if sensor.verbose:
                BLESensor.clear_dots()
                sensor.sense_message()
            manif_data = adv_data.manufacturer_data
            if sensor.manifacture_id in manif_data:
                payload = manif_data[sensor.manifacture_id]
                sensor.decode(payload)
                del BLESensor._SCANNING[device.address]
        elif BLESensor._ARGS.verbose:
            BLESensor.print_dot()

    @staticmethod
    async def _scan_devices() -> None:
        scanner = BleakScanner(detection_callback=BLESensor._device_found)
        timeout = time.time() + BLESensor._ARGS.ble_timeout
        while time.time() < timeout and len(BLESensor._SCANNING) > 0:
            await scanner.start()
            await asyncio.sleep(1)
            await scanner.stop()

    def __init__(self, name: str, manif_id: int, config: dict):
        super().__init__(name, config)
        ble = config.get("ble", None)
        if type(ble) != dict:
            raise ValueError("sensor.{:s} must have ble table".format(name))
        macaddr = ble.get("macaddr", ble)
        if type(macaddr) != str:
            raise ValueError("sensor.{:s}.ble must have macaddr".format(name))
        self._macaddr = macaddr.upper()
        self._manif_id = manif_id
        if not self.disabled:
            BLESensor._BLE_SENSORS[self._macaddr] = self

    @property
    def macaddr(self) -> str:
        return self._macaddr

    @property
    def manifacture_id(self) -> int:
        return self._manif_id

    def decode(self, payload: bytearray) -> None:
        pass
