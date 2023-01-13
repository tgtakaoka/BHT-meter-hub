import ambient

from . import Datastore


class AmbientStore(Datastore):
    @staticmethod
    def create(name: str, config: dict) -> "AmbientStore":
        channel = config.get("channel", None)
        if type(channel) != dict:
            raise ValueError("datastore.{:s} must have channel table".format(name))
        channel_id = channel.get("id", None)
        if type(channel_id) != int:
            raise ValueError("datastore.{:s}.channel must have id number".format(name))
        write_key = channel.get("write_key", None)
        if type(write_key) != str:
            raise ValueError("datastore.{:s}.channel must have write_key".format(name))
        return AmbientStore(name, channel_id, write_key, config)

    def __init__(self, name: str, channel_id: int, write_key: str, config: dict):
        super().__init__(name, config)
        self._channel_id = channel_id
        self._write_key = write_key
        self._read_key = config["channel"].get("read_key", None)

    def add_data(self, data: dict, line: dict, val, epoch_milli: int) -> None:
        self.add_data_message(line, val)
        if not self in data:
            data[self] = {"created": epoch_milli}
        tag = line["tag"]
        data[self][tag] = val

    def send_data(self, data: dict) -> None:
        if self.verbose:
            print("{:s}: {:d} ({:s})".format(self.datastore_class, self._channel_id, self.name))
            print("   {:s}".format(str(data)))
        if not self.do_store:
            return
        am = ambient.Ambient(self._channel_id, self._write_key)
        r = am.send(data)
