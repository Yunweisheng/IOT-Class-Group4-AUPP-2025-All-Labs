import network
import time
import random
from umqtt.simple import MQTTClient
from machine import I2C, Pin
from bmp280 import BMP280   # Make sure bmp280.py is also uploaded!

# =====================================================
# Configuration
# =====================================================
SSID = "Robotic WIFI"          # ⚠️ Must be 2.4 GHz Wi-Fi
PASSWORD = "rbtWIFI@2025"

BROKER = "test.mosquitto.org"
PORT = 1883
CLIENT_ID = b"esp32_gp4"
TOPIC = b"/aupp/esp32/random"
KEEPALIVE = 30

SEA_LEVEL_PRESSURE = 1013.25  # hPa for altitude calculation


# =====================================================
# Wi-Fi Handling
# =====================================================
def wifi_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        wlan.disconnect()
        time.sleep(1)

    print("🔌 Connecting to Wi-Fi:", SSID)
    wlan.connect(SSID, PASSWORD)
    start = time.ticks_ms()

    while not wlan.isconnected():
        print(".", end="")
        if time.ticks_diff(time.ticks_ms(), start) > 30000:
            print("\n⚠️ Wi-Fi connect timeout — restarting interface.")
            wlan.active(False)
            time.sleep(2)
            wlan.active(True)
            raise RuntimeError("Wi-Fi connection failed")
        time.sleep(0.5)

    print("\n✅ Wi-Fi connected:", wlan.ifconfig())
    return wlan


def ensure_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("\n📶 Wi-Fi lost, reconnecting...")
        wifi_connect()


# =====================================================
# MQTT Handling
# =====================================================
def make_client():
    return MQTTClient(client_id=CLIENT_ID, server=BROKER, port=PORT, keepalive=KEEPALIVE)


def connect_mqtt(client):
    for attempt in range(3):
        try:
            client.connect()
            print("✅ MQTT connected to", BROKER)
            return
        except OSError as e:
            print(f"⚠️ MQTT connect attempt {attempt+1}/3 failed:", e)
            time.sleep(3)
    raise RuntimeError("❌ Unable to connect to MQTT broker after 3 attempts")


# =====================================================
# BMP280 Sensor Setup
# =====================================================
def init_bmp280():
    try:
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))   # Adjust pins for your board if needed
        bmp = BMP280(i2c)
        print("✅ BMP280 detected at address", hex(bmp.addr))
        return bmp
    except Exception as e:
        print("🚫 BMP280 not found:", e)
        return None


def read_bmp280(bmp):
    try:
        temp = bmp.temperature            # °C
        pres_pa = bmp.pressure            # Pressure in Pascals
        pres_hpa = pres_pa / 100.0        # Convert to hPa
        alt = 44330.0 * (1.0 - pow(pres_hpa / SEA_LEVEL_PRESSURE, 0.1903))
        return temp, pres_hpa, alt
    except Exception as e:
        print("⚠️ Sensor read error:", e)
        return None, None, None

# =====================================================
# Main Loop
# =====================================================
def main():
    try:
        wifi_connect()
    except Exception as e:
        print("🚫 Wi-Fi Error:", e)
        print("💡 Use a 2.4 GHz hotspot or check your password.")
        return

    bmp = init_bmp280()
    if bmp is None:
        print("❌ Cannot start main loop — BMP280 not detected.")
        return

    client = make_client()

    while True:
        try:
            ensure_wifi()
            connect_mqtt(client)

            while True:
                ensure_wifi()
                temp, pres, alt = read_bmp280(bmp)

                if temp is not None:
                    payload = (
                        '{{"temperature": {:.2f}, "pressure": {:.2f}, "altitude": {:.2f}}}'
                        .format(temp, pres, alt)
                    )
                    client.publish(TOPIC, payload)
                    print("📤 Published:", payload)
                else:
                    print("⚠️ Skipped publish (invalid sensor data)")

                time.sleep(5)

        except Exception as e:
            print("⚠️ Connection error:", e)
            try:
                client.disconnect()
            except:
                pass
            print("🔁 Reconnecting in 5 s...")
            time.sleep(5)
            client = make_client()


# =====================================================
# Run
# =====================================================
main()
