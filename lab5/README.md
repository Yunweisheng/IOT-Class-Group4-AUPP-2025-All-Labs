LAB 5 – Mobile App DC Motor Control with Grafana

This project demonstrates remote control of a DC motor using an Android mobile application (MIT App Inventor) and an ESP32 web server. All motor actions are logged into InfluxDB and visualized on a Grafana dashboard.

Features
Mobile App Control

Forward / Backward / Stop buttons

Speed slider (0–100%)

ESP32 + L298N Motor Driver

HTTP endpoints for motor commands

PWM-based speed control

Accessible from MIT App and web browser

IoT Data Logging

Logs direction, speed, and timestamp to InfluxDB

Supports HTTP posting via Node-RED or direct API

Grafana Dashboard

Real-time speed graph

Command/event table

Last motor action widget

Tech Stack

Hardware: ESP32, L298N motor driver, DC motor, external power supply

Firmware: MicroPython (main.py)

Mobile App: MIT App Inventor (.aia file)

Backend: InfluxDB (via HTTP API / Node-RED)

Dashboard: Grafana

Quick Start
1. ESP32 Setup

Flash MicroPython firmware

Upload main.py

Update inside the code:

Wi-Fi SSID & password

InfluxDB/Node-RED HTTP endpoint

Motor control pins

2. Mobile App Setup

Import the .aia file into MIT App Inventor

Update the ESP32 URL:

http://<ESP32_IP>/


Build and install the APK on your Android device

3. Data Logging & Dashboard

Configure the HTTP receiver → InfluxDB

Create a database and measurement for logging

Create Grafana panels:

Motor Speed vs Time

Command History Table

Event Logs

Project Structure
.
├── main.py                     # ESP32 MicroPython firmware
├── app/
│   └── dc_motor_controller.aia # MIT App Inventor project
├── assets/                     # Diagrams, screenshots, images
│   ├── wiring-diagram.jpg
│   ├── app-layout.jpg
│   ├── grafana-dashboard.jpg
│   └── demo-thumbnail.jpg
└── README.md

Demo Videos
Video 1 – Mobile App DC Motor Control

https://youtu.be/wTxYRNPJqnc

Video 2 – ESP32 + Grafana Full Demonstration

https://youtube.com/watch?feature=shared&v=t5oU7SnD8R8

Wiring Diagram

(Place your actual diagram inside assets/wiring-diagram.jpg)

ESP32 → L298N
---------------------
GPIO 14  → IN1
GPIO 27  → IN2
GPIO 26  → ENA (PWM)
5V       → 5V
GND      → GND
Motor +  → OUT1
Motor –  → OUT2

Mobile App UI

Include screenshot: assets/app-layout.jpg

Grafana Dashboard Example

Include screenshot: assets/grafana-dashboard.jpg
