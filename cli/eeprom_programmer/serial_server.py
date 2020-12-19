import enum
import abc

from .serial_interface import SerialInterface


class ServerNotConnectedException(Exception):
    pass


class UnexpectedSignalException(Exception):
    pass


class SerialRPC(abc.ABC):
    def __init__(self, rpc_id: int):
        self._rpc_id = rpc_id

    @abc.abstractmethod
    def communicate(self, interface: SerialInterface) -> object:
        pass


class SerialServer(object):

    class Signals(enum.Enum):
        SYN = ord("s")
        ACK = ord("a")
        ERR = ord("e")
        RST = ord("r")
        FIN = ord("f")
        BYE = ord("b")

        @staticmethod
        def has_value(value: int) -> bool:
            try:
                SerialServer.Signals(value)
                return True
            except ValueError:
                return False

    def __init__(self, port, baudrate, timeout, write_timeout, debug):
        self._is_connected = False
        self._interface = SerialInterface(port, baudrate, timeout, write_timeout, debug)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.disconnect()
        except Exception as e:
            # Raise exception only if we won't shadow any previous one.
            if exc_type is None and exc_val is None and exc_tb is None:
                raise e

    def connect(self):
        if self.is_connected:
            return self

        self._interface.open()
        self._send_signal(SerialServer.Signals.SYN)
        self._recv_signal(SerialServer.Signals.ACK)
        self._is_connected = True

        return self

    def disconnect(self) -> None:
        if not self.is_connected:
            return

        self._is_connected = False
        self._send_signal(SerialServer.Signals.BYE)
        self._recv_signal(SerialServer.Signals.BYE)
        self._interface.close()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def call(self, rpc: SerialRPC):
        if not self.is_connected:
            raise ServerNotConnectedException("Cannot send rpc call without connecting to the server first.")

        self._interface.write_i8(rpc._rpc_id)
        self._recv_signal(SerialServer.Signals.ACK)
        output = rpc.communicate(self._interface)
        self._recv_signal(SerialServer.Signals.FIN)
        return output

    def _recv_signal(self, signal: Signals) -> None:
        byte = self._interface.read_i8()
        if byte != signal.value:
            name = "known"
            if SerialServer.Signals.has_value(byte):
                name = SerialServer.Signals(byte).name
            raise UnexpectedSignalException("Expected {ex_name}({ex_val}), received {recv_name}({recv_val}).".format(
                ex_name=signal.name,
                ex_val=signal.value,
                recv_name=name,
                recv_val=byte,
            ))

    def _send_signal(self, signal: Signals) -> None:
        self._interface.write_i8(signal.value)


