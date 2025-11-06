# 🌐 ESP32 → MQTT → Node-RED → InfluxDB → Grafana Dashboard

This project demonstrates a complete **IoT data pipeline** where an **ESP32** running **MicroPython** sends random sensor data through **MQTT** to **Node-RED**, which stores it in **InfluxDB** and visualizes it in **Grafana**.

---

## 🧭 Project Overview

**Flow:**
ESP32 → MQTT Broker → Node-RED → InfluxDB → Grafana

- **ESP32** publishes random sensor values to an MQTT topic.  
- **Node-RED** subscribes to the topic, processes the data, and sends it to **InfluxDB**.  
- **InfluxDB** stores time-series data efficiently.  
- **Grafana** visualizes real-time readings in a live dashboard.

---

## ⚙️ System Architecture

```mermaid
graph LR
A[ESP32 (MicroPython)] -->|Publish via MQTT| B((MQTT Broker))
B --> C[Node-RED Flow]
C --> D[(InfluxDB Database)]
D --> E[Grafana Dashboard]
