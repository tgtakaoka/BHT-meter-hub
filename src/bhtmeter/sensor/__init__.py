from importlib import import_module

from bhtmeter.datastore import Datastore
from bhtmeter.utils.snake_case import snake_case


class Sensor(object):
    _SENSORS = []

    @staticmethod
    def create(name: str, config: dict) -> "Sensor":
        sensor_class = config.get("class", None)
        if not sensor_class:
            raise ValueError("sensor.{:s} has no class defined".format(name))
        if type(sensor_class) != str:
            raise ValueError("sensor.{:s}.class must be string".format(name))
            return None
        try:
            import_path = "bhtmeter.sensor." + snake_case(sensor_class)
            module = import_module(import_path)
            class_obj = getattr(module, sensor_class)
            factory_method = getattr(class_obj, "create")
            return factory_method(name, config)
        except ModuleNotFoundError:
            pass
        raise ValueError("sensor.{:s} has unknown class {:s}".format(name, sensor_class))

    @staticmethod
    def sensors() -> list:
        return Sensor._SENSORS

    def __init__(self, name: str, config: dict):
        self._name = name
        self._description = config.get("description", None)
        self._disabled = config.get("disabled", False)
        self._args = config.get("args")
        self._data = {}
        Sensor._SENSORS.append(self)

    @property
    def sensor_class(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def disabled(self) -> bool:
        return self._disabled

    @property
    def do_sense(self) -> bool:
        return self._args.sense

    @property
    def verbose(self) -> bool:
        return self._args.verbose

    @property
    def current_data(self) -> dict:
        return self._data

    @current_data.setter
    def current_data(self, data: dict) -> None:
        self._data = data

    @property
    def sense_milli(self):
        return self.current_data.get("milli", 0)

    def sense_data(self) -> None:
        pass

    def sense_message(self):
        if self.verbose:
            print("sensing data from {:s} ({:s})".format(self.name, self.sensor_class))

    def display(self) -> None:
        pass

    def _gather_data(self, data: dict, name: str, val, epoch_milli: int) -> None:
        if not name:
            return
        for line in Datastore.dataline(name):
            datastore = line["datastore"]
            datastore.add_data(data, line, val, epoch_milli)
