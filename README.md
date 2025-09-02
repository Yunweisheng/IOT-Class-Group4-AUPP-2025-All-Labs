# IOT-Class-AUPP-2025-Hun-Teng-Group4
# 🌡️ ESP32/ESP8266 Telegram Temperature Bot with Relay Control

This project connects an ESP32/ESP8266 with a **DHT11/DHT22 temperature sensor** and a **relay module**, controlled via a Telegram bot.  
It reads temperature, sends alerts, and lets you control the relay remotely from **Telegram chats or groups**.

---

## ✨ Features

- ✅ **Temperature Monitoring**  
  Reads temperature and humidity from a DHT sensor.

- ✅ **Alerting System**
  - Sends alerts **only when temp > 30°C**.  
  - If **relay is OFF and temp > 30°C**, bot alerts **every 5 seconds** until relay is turned ON.  
  - If **relay is ON and temp > 30°C**, it sends one warning and reminders every **5 minutes**.  
  - Sends a **“Back to normal”** message when temp ≤ 30°C.

- ✅ **Relay Control**
  - `/on` → Turns relay ON.  
    - If temp > 30°C, **auto-off** is armed.  
    - Relay will **turn off automatically** once temperature drops ≤ 30°C.  
  - `/off` → Turns relay OFF immediately.  

- ✅ **Telegram Bot Commands**
