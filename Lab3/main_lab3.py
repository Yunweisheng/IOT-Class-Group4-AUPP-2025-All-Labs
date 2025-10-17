# main.py — ESP32 + BMP280 → ThingsBoard Cloud
import network, time, json
from umqtt.simple import MQTTClient
from bmp280_read import BMP280Sensor

# ===== Wi-Fi credentials =====
SSID = "Robotic WIFI"
PASSWORD = "rbtWIFI@2025"

# ===== ThingsBoard MQTT settings =====
THINGSBOARD_HOST = "mqtt.thingsboard.cloud"
THINGSBOARD_PORT = 1883
ACCESS_TOKEN = "Su04hPhoU6iB8HBj97OC"   # <-- your device token

# ===== Connect Wi-Fi =====
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🌐 Connecting to Wi-Fi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    print("✅ Wi-Fi connected:", wlan.ifconfig())

# ===== Main Program =====
def main():
    connect_wifi()
    sensor = BMP280Sensor()  # from bmp280_read.py

    client = MQTTClient(
        client_id="ESP32_BMP280",
        server=THINGSBOARD_HOST,
        port=THINGSBOARD_PORT,
        user=ACCESS_TOKEN,
        password=""
    )

    client.connect()
    print("✅ Connected to ThingsBoard Cloud")

    while True:
        try:
            temp, pres, alt = sensor.read_data()
            data = {
                "temperature": round(temp, 2),
                "pressure": round(pres, 2),
                "altitude": round(alt, 2)
            }
            payload = json.dumps(data)
            client.publish("v1/devices/me/telemetry", payload)
            print("📤 Published:", payload)
        except Exception as e:
            print("⚠️ Publish failed:", e)
        time.sleep(5)

# ===== Run =====
try:
    main()
except KeyboardInterrupt:
    print("🛑 Program stopped by user.")

