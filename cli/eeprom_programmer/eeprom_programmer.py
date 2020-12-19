import contextlib
from .serial_interface import SerialInterface
from .serial_server import SerialServer, SerialRPC


class MaxAddressRPC(SerialRPC):
    _RPC_ID = ord("m")

    def __init__(self):
        super().__init__(self._RPC_ID)

    def communicate(self, interface: SerialInterface) -> int:
        return interface.read_i16()


class EchoRPC(SerialRPC):
    _RPC_ID = ord("e")

    def __init__(self, msg: bytes):
        super().__init__(self._RPC_ID)
        if len(msg) > 0xff:
            raise ValueError(f"The maximum echo length is {0xff}, given {len(msg)}.")

        self._msg = msg

    def communicate(self, interface: SerialInterface) -> bytes:
        interface.write_i8(len(self._msg))
        interface.write_buffer(bytes(self._msg))
        length = interface.read_i8()
        response = interface.read_buffer(length)
        return response


class ReadRPC(SerialRPC):
    _RPC_ID = ord("r")

    def __init__(self, address: int):
        super().__init__(self._RPC_ID)
        self._address = address

    def communicate(self, interface: SerialInterface) -> int:
        interface.write_i16(self._address)
        byte = interface.read_i8()
        return byte


class ReadBufferRPC(SerialRPC):
    _RPC_ID = ord("R")

    def __init__(self, address: int, length: int):
        super().__init__(self._RPC_ID)
        if length > 0xff:
            raise ValueError(f"The maximum single-read length is {0xff}, given {length}.")

        self._address = address
        self._length = length

    def communicate(self, interface: SerialInterface) -> bytes:
        interface.write_i16(self._address)
        interface.write_i8(self._length)
        return interface.read_buffer(self._length)


class WriteRPC(SerialRPC):
    _RPC_ID = ord("w")

    def __init__(self, address: int, value: int):
        super().__init__(self._RPC_ID)
        self._address = address
        self._value = value

    def communicate(self, interface: SerialInterface) -> None:
        interface.write_i16(self._address)
        interface.write_i8(self._value)


class WriteBufferRPC(SerialRPC):
    _RPC_ID = ord("W")

    def __init__(self, address: int, buffer: bytes):
        super().__init__(self._RPC_ID)
        if len(buffer) > 0xff:
            raise ValueError(f"The maximum single-write length is {0xff}, given {len(buffer)}.")

        self._address = address
        self._buffer = buffer

    def communicate(self, interface: SerialInterface) -> None:
        interface.write_i16(self._address)
        interface.write_i8(len(self._buffer))
        interface.write_buffer(self._buffer)


class EEPROMProgrammer(object):

    def __init__(self, port, baudrate, timeout, write_timeout, debug):
        self._server = SerialServer(port, baudrate, timeout, write_timeout, debug)
        self._max_address = None

    @contextlib.contextmanager
    def connect(self) -> None:
        with self._connect_to_server():
            yield

    @contextlib.contextmanager
    def _connect_to_server(self) -> SerialServer:
        with self._server.connect():
            yield self._server

    @property
    def max_address(self) -> int:
        if self._max_address is not None:
            return self._max_address

        with self._connect_to_server() as server:
            self._max_address = server.call(MaxAddressRPC())
            return self._max_address

    def echo(self, msg: bytes) -> bytes:
        with self._connect_to_server() as server:
            return server.call(EchoRPC(msg))

    def read(self, address: int) -> int:
        if address > self.max_address:
            raise ValueError("Exceeded maximum EEPROM memory address({}), given: {}.".format(
                self.max_address,
                address
            ))

        with self._connect_to_server() as server:
            return server.call(ReadRPC(address))

    def read_buffer(self, address: int, length: int):
        if address + length > self.max_address:
            raise ValueError("Exceeded maximum EEPROM memory address({}), given: address({})+length({}).".format(
                self.max_address,
                address,
                length
            ))

        with self._connect_to_server() as server:
            return server.call(ReadBufferRPC(address, length))

    def write(self, address: int, data: int):
        if address > self.max_address:
            raise ValueError("Exceeded maximum EEPROM memory address({}), given: {}.".format(
                self.max_address,
                address
            ))

        with self._connect_to_server() as server:
            return server.call(WriteRPC(address, data))

    def write_buffer(self, address: int, buffer: bytes):
        if address + len(buffer) > self.max_address:
            raise ValueError("Exceeded maximum EEPROM memory address({}), given: address({})+length({}).".format(
                self.max_address,
                address,
                len(buffer)
            ))

        with self._connect_to_server() as server:
            return server.call(WriteBufferRPC(address, buffer))
