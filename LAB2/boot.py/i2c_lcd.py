import time
from lcd_api import LcdApi
from machine import I2C

class I2cLcd(LcdApi):
    # PCF8574 pin definitions
    MASK_RS = 0x01
    MASK_RW = 0x02
    MASK_E  = 0x04
    MASK_BACKLIGHT = 0x08

    SHIFT_DATA = 4

    # -----------------------------
    # Add move_to for cursor positioning
    # -----------------------------
    def move_to(self, col, row):
        row_offsets = [0x00, 0x40, 0x14, 0x54]  # DDRAM offsets for 4 lines
        if row > self.num_lines - 1:
            row = self.num_lines - 1
        addr = col + row_offsets[row]
        self.hal_write_command(self.LCD_DDRAM | addr)

    # -----------------------------
    # Constructor
    # -----------------------------
    def init(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = self.MASK_BACKLIGHT
        self.busy_flag = 0

        time.sleep_ms(20)   # Wait for LCD power up
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_us(100)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x02)

        self.hal_write_command(self.LCD_FUNCTION |
                               self.LCD_FUNCTION_2LINES)
        self.hal_write_command(self.LCD_ON_CTRL |
                               self.LCD_ON_DISPLAY)
        self.hal_write_command(self.LCD_ENTRY_MODE |
                               self.LCD_ENTRY_INC)
        self.clear()

    # -----------------------------
    # Low-level LCD functions
    # -----------------------------
    def hal_write_init_nibble(self, nibble):
        byte = (nibble << self.SHIFT_DATA) & 0xF0
        self.hal_write_byte(byte)

    def hal_backlight_on(self):
        self.backlight = self.MASK_BACKLIGHT
        self.hal_write_byte(0)

    def hal_backlight_off(self):
        self.backlight = 0x00
        self.hal_write_byte(0)

    def hal_write_command(self, cmd):
        self.hal_write_byte((cmd & 0xF0) | self.MASK_RS*0)
        self.hal_write_byte(((cmd << 4) & 0xF0) | self.MASK_RS*0)

    def hal_write_data(self, data):
        self.hal_write_byte((data & 0xF0) | self.MASK_RS)
        self.hal_write_byte(((data << 4) & 0xF0) | self.MASK_RS)

    def hal_write_byte(self, byte):
        self.i2c.writeto(self.i2c_addr, bytes([byte | self.backlight | self.MASK_E]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([(byte | self.backlight) & ~self.MASK_E]))
        time.sleep_us(50)

    def hal_sleep_us(self, usecs):
        time.sleep_us(usecs)