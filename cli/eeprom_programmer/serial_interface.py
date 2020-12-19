import struct
import serial
import time
import glob
import sys


class SerialInterface(object):
    _BIT_ORDER = "<"

    def __init__(self, port, baudrate, timeout, write_timeout, debug=False):
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._write_timeout = write_timeout
        self._debug = debug
        self._serial = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except Exception as e:
            # Raise exception only if we won't shadow any previous one.
            if exc_type is None and exc_val is None and exc_tb is None:
                raise e

    def open(self):
        if self._serial is None:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout,
                writeTimeout=self._write_timeout
            )

            # The serial port might take a while before we can send/recv any data
            time.sleep(2)

    def close(self):
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read_buffer(self, length: int) -> bytes:
        buffer = self._serial.read(length)
        if self._debug:
            print("<", buffer)

        return buffer

    def read_i8(self) -> int:
        buffer = self.read_buffer(1)
        return struct.unpack(self._BIT_ORDER + "B", buffer)[0]

    def read_i16(self) -> int:
        buffer = self.read_buffer(2)
        return struct.unpack(self._BIT_ORDER + "H", buffer)[0]

    def read_i32(self) -> int:
        buffer = self.read_buffer(4)
        return struct.unpack(self._BIT_ORDER + "L", buffer)[0]

    def read_string(self):
        buffer = []
        byte = b""
        while byte != b"\x00":
            byte = self.read_buffer(1)
            buffer.append(byte)

        return str(b"".join(buffer), encoding="ASCII")

    def write_buffer(self, buffer: bytes) -> None:
        if self._debug:
            print(">", buffer)

        self._serial.write(buffer)

    def write_i8(self, value: int):
        buffer = struct.pack(self._BIT_ORDER + "B", value)
        self.write_buffer(buffer)

    def write_i16(self, value: int):
        buffer = struct.pack(self._BIT_ORDER + "H", value)
        self.write_buffer(buffer)

    def write_i32(self, value: int):
        buffer = struct.pack(self._BIT_ORDER + "L", value)
        self.write_buffer(buffer)

    def write_string(self, string: str) -> None:
        buffer = bytes(string, encoding="ASCII")
        buffer = buffer + b"\x00"
        self.write_buffer(buffer)


# From https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
def get_serial_ports():
    """
    Lists serial ports.
    :return: ([str]) A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    results = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            results.append(port)
        except (OSError, serial.SerialException):
            pass
    return results
