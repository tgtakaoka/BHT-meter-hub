import os
import sys

import tomli

from bhtmeter.datastore import Datastore
from bhtmeter.sensor import Sensor
from bhtmeter.utils.merge_toml import merge_toml


class Config(object):
    """
    Configuration file of python-bhtmeter project.

    [datastore.<datastore_name>]
    class = "<datastore_class>"
    description = "<description>"
    data.<tag> = "<line_name>"

    [sensor.<sensor_name>]
    class = "<sensor_class>"
    description = "<description>"
    data.<value_name> = "<line_name>"
    """

    def __init__(self, args):
        self._args = args
        self._config = {"args": args}

    def load(self) -> bool:
        for file in self._args.config:
            if self.verbose:
                print("load configuration file {:s}".format(file))
            try:
                with open(file, "rb") as f:
                    config = tomli.load(f)
                    self._config = merge_toml(self._config, config)
            except OSError as e:
                print("configuration file {:s} not found".format(file), file=sys.stderr)
                return False
        return True

    @property
    def verbose(self) -> bool:
        return self._args.verbose

    def parse(self) -> None:
        self._parse_datastores()
        self._parse_sensors()

    def _parse_datastores(self) -> None:
        datastores = self._config.get("datastore")
        if type(datastores) != dict:
            raise ValueError("no datastore is defined")
        for name in datastores:
            config = datastores[name]
            config.update({"args": self._args})
            Datastore.create(name, config)

    def _parse_sensors(self) -> None:
        sensors = self._config.get("sensor")
        if type(sensors) != dict:
            raise ValueError("no sensor is defined")
        for name in sensors:
            config = sensors[name]
            config.update({"args": self._args})
            Sensor.create(name, config)
