from importlib import import_module

from bhtmeter.utils.snake_case import snake_case


class Datastore(object):
    _DATASTORES = []
    _DATALINES = {}

    @staticmethod
    def create(name: str, config: dict) -> "Datastore":
        datastore_class = config.get("class", None)
        if not datastore_class:
            raise ValueError("datastore.{:s} has no class defined".format(name))
        if type(datastore_class) is not str:
            raise ValueError("datastore.{:s}.class must be string".format(name))
        try:
            import_path = "bhtmeter.datastore." + snake_case(datastore_class)
            module = import_module(import_path)
            class_obj = getattr(module, datastore_class)
            factory_method = getattr(class_obj, "create")
            return factory_method(name, config)
        except ModuleNotFoundError:
            pass
        raise ValueError("datastore.{:s} has unknown class {:s}".format(name, datastore_class))

    @staticmethod
    def datastores() -> list:
        return Datastore._DATASTORES

    @staticmethod
    def datalines() -> dict:
        return Datastore._DATALINES

    @staticmethod
    def dataline(name: str) -> list:
        return Datastore._DATALINES[name]

    def __init__(self, name: str, config: dict):
        self._name = name
        self._description = config.get("description", None)
        self._disabled = config.get("disabled", False)
        self._args = config.get("args")
        lines = config.get("data", None)
        if not lines:
            raise ValueError("datastore.{:s} must have data table".format(name))
        if type(lines) is not dict:
            raise ValueError("datastore.{:s}.data must be table".format(name))
        for tag in lines:
            line = lines[tag]
            if line not in Datastore._DATALINES:
                Datastore._DATALINES[line] = []
            Datastore._DATALINES[line].append({"name": line, "datastore": self, "tag": tag})
        Datastore._DATASTORES.append(self)

    @property
    def datastore_class(self) -> str:
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
    def do_store(self) -> bool:
        return self._args.store

    @property
    def verbose(self) -> bool:
        return self._args.verbose

    def add_data(self, data: dict, line: dict, val, epoch_milli: int) -> None:
        pass

    def add_data_message(self, line: dict, val) -> None:
        if self.verbose:
            name = line["name"]
            tag = line["tag"]
            print(
                "add data to {:s}:{:s} ({:s}) {:s}={:f}".format(
                    self.name, tag, self.datastore_class, name, val
                )
            )

    def send_data(self, data: dict) -> None:
        pass
