import fire
import tqdm

import eeprom_programmer


class EEPROMCLI(object):
    def __init__(self, port, baudrate=9600, timeout=2, write_timeout=0, debug=False):
        super(EEPROMCLI, self).__init__()
        self.programmer = eeprom_programmer.EEPROMProgrammer(port, baudrate, timeout, write_timeout, debug)
        self._debug = debug

    def _progress_bar(self, iterator):
        if self._debug:
            return iterator
        else:
            return tqdm.tqdm(iterator)

    def echo(self, msg: str):
        return str(self.programmer.echo(bytes(msg, encoding="ASCII")), encoding="ASCII")

    def read(self, address: int, as_hex: bool=True):
        value = self.programmer.read(address)
        return "{:#04x}".format(value) if as_hex else value

    def write(self, address: int, *data: list):
        # self.programmer.write(address, data)
        pass

    def print(self, start=0x0000, length=0x00ff):
        eeprom_data = []
        remaining_end = (start + length) % 16
        end = start + length - remaining_end
        with self.programmer.connect():
            for i in self._progress_bar(range(start, end, 16)):
                eeprom_data.extend([b for b in self.programmer.read_buffer(i, 16)])

            for i in range(remaining_end + 1):
                eeprom_data.append(self.programmer.read(end + i))

        for i in range(0, length, 16):
            bytes_in_line = min(length - i + 1, 16)
            print("{:#06x}".format(start + i), end=": ")
            for j in range(bytes_in_line):
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
