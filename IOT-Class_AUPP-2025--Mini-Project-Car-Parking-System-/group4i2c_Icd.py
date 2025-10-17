# group4i2c_lcd.py — Stable LCD driver for ESP32 + PCF8574 I2C 16x2
from time import sleep_ms
import lcd_api

LCD_CLR = 0x01
LCD_HOME = 0x02
LCD_ENTRY_MODE = 0x04
LCD_DISPLAY_CTRL = 0x08
LCD_FUNCTION_SET = 0x20
LCD_SET_DDRAM = 0x80
ENTRY_LEFT = 0x02
ENTRY_SHIFT_DECREMENT = 0x00
DISPLAY_ON = 0x04
CURSOR_OFF = 0x00
BLINK_OFF = 0x00
FUNCTION_2LINE = 0x08
FUNCTION_5x8DOTS = 0x00
ENABLE = 0x04
BACKLIGHT = 0x08

class I2cLcd(lcd_api.LcdApi):
    def __init__(self, i2c, addr, num_lines=2, num_columns=16):
        self.i2c = i2c
        self.addr = addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = BACKLIGHT
        self._init_lcd()

    def _write(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.backlight]))

    def _pulse(self, data):
        self._write(data | ENABLE)
        sleep_ms(2)
        self._write(data & ~ENABLE)
        sleep_ms(2)

    def hal_write_command(self, cmd):
        self._send(cmd, 0)

    def hal_write_data(self, data):
        self._send(data, 0x01)

    def _send(self, data, mode=0):
        high = data & 0xF0
        low = (data << 4) & 0xF0
        self._write(high | mode)
        self._pulse(high | mode)
        self._write(low | mode)
        self._pulse(low | mode)

    def _init_lcd(self):
        sleep_ms(50)
        # Reset to 4-bit mode
        for _ in range(3):
            self._write(0x30)
            self._pulse(0x30)
            sleep_ms(5)
        self._write(0x20)
        self._pulse(0x20)
        sleep_ms(5)
        # Function set, display on, clear, entry mode
        self.hal_write_command(LCD_FUNCTION_SET | FUNCTION_2LINE | FUNCTION_5x8DOTS)
        self.hal_write_command(LCD_DISPLAY_CTRL | DISPLAY_ON | CURSOR_OFF | BLINK_OFF)
        self.clear()
        self.hal_write_command(LCD_ENTRY_MODE | ENTRY_LEFT | ENTRY_SHIFT_DECREMENT)
        sleep_ms(2)

    def clear(self):
        self.hal_write_command(LCD_CLR)
        sleep_ms(3)

    def move_to(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        self.hal_write_command(LCD_SET_DDRAM | (col + row_offsets[row]))

    def putchar(self, char):
        self.hal_write_data(ord(char))
