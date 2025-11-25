# LAB 5 – Mobile App DC Motor Control with Grafana

Control a DC motor remotely using an Android app (MIT App Inventor) and an ESP32 web server, while logging all actions to InfluxDB and visualizing them in Grafana.

---

## Features

- 📱 **Mobile app control**
  - Forward / Backward / Stop buttons
  - Speed slider (0–100%)
- 🔌 **ESP32 + L298N motor driver**
  - HTTP endpoints for motor control
  - PWM speed control
- 📡 **IoT data logging**
  - Logs commands and speed to InfluxDB
- 📊 **Grafana dashboard**
  - Real-time motor speed graph
  - Last command & event table

---

## Tech Stack

- **Hardware:** ESP32, L298N, DC motor, external power supply  
- **Firmware:** MicroPython (`main.py`)  
- **App:** MIT App Inventor (`.aia` project)  
- **Backend:** InfluxDB (via HTTP / Node-RED or similar)  
- **Dashboard:** Grafana

---

## Quick Start

1. **ESP32**
   - Flash MicroPython and upload `main.py`
   - Set your Wi-Fi SSID/password and server URLs inside the code
2. **Mobile App**
   - Import the `.aia` file into MIT App Inventor
   - Set base URL to `http://<ESP32_IP>/`
   - Build and install the APK on your Android phone
3. **Data Logging & Dashboard**
   - Configure your HTTP endpoint → InfluxDB
   - Open Grafana and connect it to InfluxDB
   - Import/create panels for:
     - Motor speed vs time
     - Last command
     - Event table

---

## Project Structure

```text
.
├── main.py                     # ESP32 MicroPython code
├── app/
│   └── dc_motor_controller.aia # MIT App Inventor project
├── assets/                     # Images / screenshots
│   ├── wiring-diagram.jpg
│   ├── app-layout.jpg
│   ├── grafana-dashboard.jpg
│   └── demo-thumbnail.jpg
└── README.md

[Demo Video – Mobile DC Motor Control](https://your-demo-video-link-here)

[![Demo Video](assets/demo-thumbnail.jpg)](https://your-demo-video-link-here)


### Wiring & Setup
![Wiring Diagram](assets/wiring-diagram.jpg)

### Mobile App UI
![Mobile App Layout](assets/app-layout.jpg)

### Grafana Dashboard
![Grafana Dashboard](assets/grafana-dashboard.jpg)
