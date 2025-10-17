# bmp280.py — BMP280 sensor driver (MicroPython)
import struct
from machine import I2C

class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr
        self.dig = {}
        self._load_calibration()
        # normal mode, oversampling x1, filter off
        self.i2c.writeto_mem(self.addr, 0xF4, b'\x27')
        self.i2c.writeto_mem(self.addr, 0xF5, b'\xA0')

    def _load_calibration(self):
        calib = self.i2c.readfrom_mem(self.addr, 0x88, 24)
        vals = struct.unpack("<HhhHhhhhhhhh", calib)
        names = ['T1','T2','T3','P1','P2','P3','P4','P5','P6','P7','P8','P9']
        self.dig = dict(zip(names, vals))

    def _read_raw_data(self):
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        adc_p = ((data[0] << 16) | (data[1] << 8) | data[2]) >> 4
        adc_t = ((data[3] << 16) | (data[4] << 8) | data[5]) >> 4
        return adc_t, adc_p

    @property
    def temperature(self):
        adc_t, _ = self._read_raw_data()
        d = self.dig
        var1 = (((adc_t / 16384.0) - (d['T1'] / 1024.0)) * d['T2'])
        var2 = ((((adc_t / 131072.0) - (d['T1'] / 8192.0)) ** 2) * d['T3'])
        self.t_fine = var1 + var2
        return self.t_fine / 5120.0

    @property
    def pressure(self):
        _, adc_p = self._read_raw_data()
        d = self.dig
        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * d['P6'] / 32768.0
        var2 = var2 + var1 * d['P5'] * 2.0
        var2 = var2 / 4.0 + d['P4'] * 65536.0
        var1 = (d['P3'] * var1 * var1 / 524288.0 + d['P2'] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * d['P1']
        if var1 == 0:
            return 0
        p = 1048576.0 - adc_p
        p = ((p - var2 / 4096.0) * 6250.0) / var1
        var1 = d['P9'] * p * p / 2147483648.0
        var2 = p * d['P8'] / 32768.0
        p = p + (var1 + var2 + d['P7']) / 16.0
        return p / 100  # hPa

