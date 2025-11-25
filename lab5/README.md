# LAB 5 – Mobile App DC Motor Control with Grafana

This project demonstrates remote control of a DC motor using an Android mobile application (MIT App Inventor) and an ESP32 web server. All motor actions are logged into InfluxDB and visualized on a Grafana dashboard.

---

## Features

### Mobile App Control
- Forward / Backward / Stop buttons  
- Speed slider  
- Sends HTTP requests directly to ESP32

### ESP32 + L298N Motor Driver
- HTTP endpoints for motor commands  
- PWM-based speed control  
- Works with both web browser and MIT App Inventor

### IoT Data Logging
- Logs direction, speed, and timestamp to InfluxDB  
- Supports HTTP posting via Node-RED or direct API

### Grafana Dashboard
- Real-time motor speed graph  
- Command and event history  
- Last motor action widget  

---

## ⚠ MIT App Inventor Speed Control Notice  
MIT App Inventor’s slider and HTTP request timing can only reliably control speed between:

- **MAX SPEED = 50**  
- **MIN SPEED = 0**

Speed values above 50 may cause delay, command loss, or unstable PWM timing inside the MIT App Inventor environment.

---

## Tech Stack

- **Hardware:** ESP32, L298N, DC motor, external power supply  
- **Firmware:** MicroPython (`main.py`)  
- **Mobile App:** MIT App Inventor (`dc_motor_controller.aia`)  
- **Backend:** InfluxDB (via Node-RED/HTTP API)  
- **Dashboard:** Grafana  

---

# Demo Videos  
Click on any video thumbnail below to watch the demonstration.

### **Video 1 – Mobile App DC Motor Control**  
[![Video 1](https://img.youtube.com/vi/wTxYRNPJqnc/0.jpg)](https://youtu.be/wTxYRNPJqnc)

---

### **Video 2 – ESP32 + Grafana Full Demonstration**  
[![Video 2](https://img.youtube.com/vi/t5oU7SnD8R8/0.jpg)](https://youtube.com/watch?v=t5oU7SnD8R8)

---

## Quick Start Guide

### 1. ESP32 Setup
1. Flash MicroPython firmware  
2. Upload `main.py`  
3. Update the following inside the code:
   - Wi-Fi SSID & password  
   - Node-RED / InfluxDB endpoint  
   - Motor control GPIO pins  

---

## 3. Grafana Dashboard  
![Grafana Dashboard](https://github.com/user-attachments/assets/2a2808d8-aa69-49c1-987b-8b1d101fa93e)

---

## 4. Mobile UI (MIT App Inventor)
![MIT App UI](https://github.com/user-attachments/assets/9c9a7746-950c-4012-9064-f78194974410)

---

## Wiring Diagram

### Diagram 1
![Diagram 1](images/image.png)

### Diagram 2
![Diagram 2](images/image1.png)

### Diagram 3
![Diagram 3](images/image2.png)

---

## Project Structure

