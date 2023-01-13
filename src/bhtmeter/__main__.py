import argparse

from bhtmeter.config import Config
from bhtmeter.datastore import Datastore
from bhtmeter.sensor import Sensor
from bhtmeter.sensor.ble_sensor import BLESensor


def main():
    parser = argparse.ArgumentParser(prog="bhtmeter")
    parser.add_argument(
        "config_files",
        metavar="<config_toml>",
        type=str,
        nargs="+",
        help="configuration files",
    )
    parser.add_argument("-v", "--verbose", help="increase output vervbosity", action="store_true")
    parser.add_argument(
        "--sense",
        default=False,
        help="sense data from sensor",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--display",
        default=False,
        help="display sensed data",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--store",
        default=False,
        help="store data to datastore",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--ble_timeout",
        type=int,
        default=30,
        help="timeout seconds for BLE scan",
        action="store",
    )
    args = parser.parse_args()

    config = Config(args)
    if not config.load():
        exit
    config.parse()

    BLESensor.scan_sensors(args)
    send_data = {}
    for sensor in Sensor.sensors():
        if not sensor.disabled:
            sensor.sense_data()
            sensor.gather_data(send_data)

    for sensor in Sensor.sensors():
        if not sensor.disabled:
            if args.display:
                sensor.display()

    for datastore in Datastore.datastores():
        if datastore not in send_data:
            continue
        datastore.send_data(send_data[datastore])
