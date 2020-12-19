import fire
import tqdm

import eeprom_programmer


class EEPROMCLI(object):
    def __init__(self, port: str, baudrate: int=9600, timeout: int=2, write_timeout: int=0, debug: bool=False):
        super(EEPROMCLI, self).__init__()
        self.programmer = eeprom_programmer.EEPROMProgrammer(port, baudrate, timeout, write_timeout, debug)
        self._debug = debug

    def _progress_bar(self, iterator, total: int=None, step: int=1):
        if self._debug:
            return iterator
        else:
            return tqdm.tqdm(iterator, total=total/step, unit_scale=step, unit="Bytes")

    @staticmethod
    def _bytes_range(start, end, size):
        current = start
        while current + size < end:
            yield current, size
            current += size

        remainder = end - current
        if remainder > 0:
            yield current, remainder

    def echo(self, msg: str):
        return str(self.programmer.echo(bytes(msg, encoding="ASCII")), encoding="ASCII")

    def read(self, address: int, as_hex: bool=True):
        value = self.programmer.read(address)
        return "{:#04x}".format(value) if as_hex else value

    def write(self, address: int, *data: int):
        self.programmer.write_buffer(address, bytes(data))

    def print(self, start=0x0000, length=0x00ff):
        eeprom_data = []
        with self.programmer.connect():
            for offset, size in self._progress_bar(self._bytes_range(start, start + length, 16)):
                eeprom_data.extend([b for b in self.programmer.read_buffer(offset, size)])

        for i, size in self._bytes_range(start, start + length, 16):
            print("{:#06x}".format(start + i), end=": ")
            for j in range(size):
                print("{:#04x}".format(eeprom_data[i + j]), end=" ")

            print("")

    def zero(self, start: int, end: int):
        with self.programmer.connect():
            for i in self._progress_bar(range(start, end + 1)):
                self.write(i, 0)

    def dump(self, path: str):
        with open(path, "wb") as out_file:
            with self.programmer.connect():
                for i in self._progress_bar(range(0, self.programmer.max_address, 16)):
                    out_file.write(self.programmer.read_buffer(i, 16))

    @property
    def is_connected(self):
        return self.echo("PING") == "PING"

    @property
    def max_address(self):
        return self.programmer.max_address

    @staticmethod
    def list_serial_ports():
        return eeprom_programmer.get_serial_ports()


if __name__ == '__main__':
    fire.Fire(EEPROMCLI)
