# 🌐 IoT Data Pipeline: ESP32 → MQTT → Node-RED → InfluxDB → Grafana

This project demonstrates a complete **IoT data monitoring system** using an **ESP32** running **MicroPython**, which sends random sensor data through **MQTT**, processed in **Node-RED**, stored in **InfluxDB**, and visualized on a live **Grafana Dashboard**.

---

## 🧭 Project Flow

**ESP32 → MQTT Broker → Node-RED → InfluxDB → Grafana**

| Component | Purpose |
|------------|----------|
| Component | Purpose | Image |
|------------|----------|-------|
| **ESP32 (MicroPython)** | Sends random sensor data every few seconds | ![ESP32](https://github.com/YourUsername/YourRepoName/blob/main/assets/esp32.jpg) |
| **MQTT (Mosquitto)** | Transfers data between ESP32 and Node-RED | ![MQTT](https://github.com/YourUsername/YourRepoName/blob/main/assets/mqtt.png) |
| **Node-RED** | Processes and forwards data to InfluxDB | ![Node-RED](https://github.com/Theara-Seng/iot_micropython/blob/main/Lab4/Image/mqtt-node_red.png) |
| **InfluxDB** | Stores time-series data from Node-RED | ![InfluxDB](https://github.com/Theara-Seng/iot_micropython/blob/main/Lab4/Image/influxdbdata.png) |
| **Grafana** | Displays real-time charts and analytics | ![Grafana](https://github.com/Theara-Seng/iot_micropython/blob/main/Lab4/Image/grafana.png) |


---

## ⚙️ Architecture Diagram

```mermaid
graph LR
A[ESP32] -->|MQTT Publish| B((MQTT Broker))
B --> C[Node-RED Flow]
C --> D[(InfluxDB Database)]
D --> E[Grafana Dashboard] here should be added video demo and add photo like grafana influx and node red 
