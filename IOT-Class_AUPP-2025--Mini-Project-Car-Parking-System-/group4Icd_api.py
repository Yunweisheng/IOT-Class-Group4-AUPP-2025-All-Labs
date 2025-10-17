# lcd_api.py - basic LCD API adapted for MicroPython
from time import sleep_ms

class LcdApi:
    def init(self):
        self.num_lines = 2
        self.num_columns = 16

    def putchar(self, char):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def move_to(self, col, row):
        raise NotImplementedError

    def putstr(self, string):
        for ch in string:
            self.putchar(ch)

    def hal_write_command(self, cmd):
        raise NotImplementedError

    def hal_write_data(self, data):
        raise NotImplementedError
