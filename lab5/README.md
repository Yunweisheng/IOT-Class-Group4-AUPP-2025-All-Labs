# LAB 5 – Mobile App DC Motor Control with Grafana

This project demonstrates how to remotely control a DC motor using an Android mobile application (MIT App Inventor) and an ESP32 web server.  
All motor commands and speed values are logged into InfluxDB and visualized in Grafana for monitoring and analysis.

---

## 1. Features

### Mobile App Control
- Forward / Backward / Stop buttons  
- Adjustable speed slider  
- Sends HTTP requests directly to the ESP32

### ESP32 + L298N Motor Driver
- REST-style HTTP endpoints for direction and speed  
- PWM-based motor speed control  
- Works with both MIT App Inventor and browser access

### IoT Data Logging
- Logs speed, direction, and timestamp to InfluxDB  
- Supports Node-RED or direct HTTP posting

### Grafana Dashboard
- Real-time speed graph  
- Last command widget  
- Event and history table

---

## ⚠ MIT App Inventor Speed Limit Notice  
Due to MIT App Inventor’s slider + HTTP timing limitations, **the Android app can only reliably control speeds between:**

- **0 (minimum)**  
- **50 (maximum recommended)**  

Values above **50** may lead to:
- delayed HTTP commands  
- unstable PWM  
- inconsistent motor response  

---

## 2. Tech Stack

| Layer | Technology |
|-------|------------|
| Hardware | ESP32, L298N, DC motor, external supply |
| Firmware | MicroPython (`main.py`) |
| Mobile App | MIT App Inventor (`dc_motor_controller.aia`) |
| Backend | InfluxDB (via Node-RED HTTP endpoint) |
| Dashboard | Grafana |

---

# 3. Demo Videos  
Click any thumbnail to watch the demonstration.

### **Mobile App DC Motor Control**  
[![Video 1](https://img.youtube.com/vi/wTxYRNPJqnc/0.jpg)](https://youtu.be/wTxYRNPJqnc)

### **ESP32 + Grafana Full Visualization**  
[![Video 2](https://img.youtube.com/vi/t5oU7SnD8R8/0.jpg)](https://youtube.com/watch?v=t5oU7SnD8R8)

---

## 4. Quick Start Guide

### Step 1 – ESP32 Setup
1. Flash MicroPython to your ESP32  
2. Upload `main.py`  
3. Configure inside the code:
   - Wi-Fi SSID + Password  
   - InfluxDB / Node-RED URL  
   - Motor GPIO pins (IN1, IN2, ENA)

---

## Step 2 – Mobile App Setup (MIT App Inventor)
1. Import the `.aia` file  
2. Set ESP32 IP address in the app:


---

## Step 3 – Grafana Dashboard  
![Grafana Dashboard](https://github.com/user-attachments/assets/2a2808d8-aa69-49c1-987b-8b1d101fa93e)

---

## Step 4 – Mobile User Interface  
![MIT App UI](https://github.com/user-attachments/assets/9c9a7746-950c-4012-9064-f78194974410)

---

# 5. Wiring Diagram & Motor Connection

### ESP32 → L298N Motor Driver

GPIO 14 → IN1 (Motor Direction A)
GPIO 27 → IN2 (Motor Direction B)
GPIO 26 → ENA (PWM) (Speed Control)

5V → 5V (L298N Logic Power)
GND → GND (Common Ground)

Motor + → OUT1
Motor – → OUT2

> **Note:**  
> The motor requires an external supply (6V–12V).  
> ESP32 GND and L298N GND must be connected together.

---

### Diagram 1  
![Diagram 1](images/image.png)

### Diagram 2  
![Diagram 2](images/image1.png)

### Diagram 3  
![Diagram 3](images/image2.png)

---



