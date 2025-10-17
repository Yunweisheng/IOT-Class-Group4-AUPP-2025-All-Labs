# bmp280_read.py — Simple BMP280 reader class
from machine import Pin, I2C
import bmp280
import math

class BMP280Sensor:
    def __init__(self, scl=22, sda=21, addr=0x76):
        # Initialize I2C and BMP280
        self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda))
        print("🔍 Scanning I2C devices...")
        devices = self.i2c.scan()
        if not devices:
            raise OSError("❌ No I2C devices found. Check wiring and power.")
        print("✅ I2C device(s) found:", [hex(d) for d in devices])
        if addr not in devices:
            addr = devices[0]
            print(f"ℹ️ Using detected I2C address: {hex(addr)}")
        self.bmp = bmp280.BMP280(self.i2c, addr=addr)
        self.sea_level_pressure = 1013.25  # hPa standard

    def read_data(self):
        temp = self.bmp.temperature
        pres = self.bmp.pressure
        alt = self.calculate_altitude(pres)
        return temp, pres, alt

    def calculate_altitude(self, pressure):
        """Calculate altitude (m) from pressure (hPa)."""
        return 44330 * (1 - (pressure / self.sea_level_pressure) ** (1 / 5.255))

