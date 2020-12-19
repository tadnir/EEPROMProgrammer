import fire
import tqdm
import os

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
            calculated_total = None if total is None else int(total/step)
            return tqdm.tqdm(iterator, total=calculated_total, unit_scale=step, unit="Bytes")

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

    def print(self, start=0x0000, length=0x0100, full: bool=False):
        eeprom_data = []
        with self.programmer.connect():
            if full:
                start = 0x0000
                length = self.programmer.memory_size

            for offset, size in self._progress_bar(
                    iterator=self._bytes_range(start, start + length, 16),
                    total=length,
                    step=16):
                eeprom_data.extend([b for b in self.programmer.read_buffer(offset, size)])

        for offset, size in self._bytes_range(start, start + length, 16):
            index = offset - start
            print("{:#06x}".format(offset), end=": ")
            for j in range(size):
                print("{:#04x}".format(eeprom_data[index + j]), end=" ")

            print("")

    def zero(self, start: int=0x0000, length: int=0x0010, value: int=0x00):
        with self.programmer.connect():
            for offset, size in self._progress_bar(
                    iterator=self._bytes_range(start, start + length, 16),
                    total=length,
                    step=16):
                self.write(offset, *([value]*size))

    def dump(self, path: str):
        with open(path, "wb") as out_file:
            with self.programmer.connect():
                for offset, size in self._progress_bar(
                        iterator=self._bytes_range(0, self.programmer.memory_size, 16),
                        total=self.programmer.memory_size,
                        step=16):
                    out_file.write(self.programmer.read_buffer(offset, size))

    def load(self, path: str):
        file_size = os.path.getsize(path)
        with self.programmer.connect():
            if file_size != self.programmer.memory_size:
                raise ValueError("Load file size must be equal to the memory size({}), given {}.".format(
                    self.programmer.memory_size,
                    file_size
                ))

            with open(path, "rb") as in_file:
                for offset, size in self._progress_bar(
                        iterator=self._bytes_range(0, self.programmer.memory_size, 16),
                        total=self.programmer.memory_size,
                        step=16):
                    self.programmer.write_buffer(offset, in_file.read(size))

    def memory_size(self, as_hex: bool=False):
        size = self.programmer.memory_size
        return hex(size) if as_hex else size

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
