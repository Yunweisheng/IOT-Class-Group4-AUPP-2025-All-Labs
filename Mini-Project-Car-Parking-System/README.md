# Smart Parking Car - Mini Project 1 🚗🏞️

## Overview

This project implements a three-slot smart parking system using an ESP32. The system includes functionality for detecting vehicles, managing parking slots, calculating parking fees, displaying live status on an LCD and a web dashboard, and sending receipts via Telegram. 

### Functional Features ⚙️

- **Entry & Gate Logic 🚪:**
  - The system uses an ultrasonic sensor to detect arriving cars.
  - Displays available slots on an LCD and opens the servo gate if space is available.
  - If all slots are occupied, the LCD shows "FULL."
  - The gate automatically closes after the car passes or after a short timeout.

- **Auto-ID Assignment 🆔:**
  - Automatically assigns one of three IDs (1–3) to cars based on the order in which they park.
  - Tracks each car's time-in and binds them to specific slots.
  
- **Exit & Billing 💸:**
  - When a car leaves, the system records the time-out, computes the duration and fee, and sends a receipt via Telegram.
  - Pricing rule: $0.50 per minute.

- **Web Dashboard 🌐:**
  - Live status of slots, including the number of free and occupied slots.
  - Displays ID, time-in, and elapsed time for occupied slots.
  - Active tickets table with ID, slot, time-in, and elapsed time.
  - Recent tickets table showing ID, slot, duration, fee, and time-out.
  - Auto-refreshes every 2–5 seconds.

- **Telegram Notifications 📲:**
  - Sends a receipt when a car exits, showing ticket details, duration, and fee.

---

## Installation 🛠️

### Requirements 📋

- **ESP32**
- **IR sensors** for detecting car presence
- **Ultrasonic sensor** for detecting car arrival
- **Servo motor** for the gate
- **LCD Display** (16x2)
- **Telegram Bot API** for notifications
- **Web browser** for dashboard access

### Dependencies 📚

1. **ESP32 Libraries**
   - Install necessary ESP32 libraries for controlling GPIO, LCD, and network features.
   
2. **Telegram Bot API**
   - Follow [this guide](https://core.telegram.org/bots#botfather) to create your bot and obtain a `BOT_TOKEN`.

3. **Web Dashboard**
   - The ESP32 serves a web dashboard that updates every 2–5 seconds.

4. **Python**
   - Install MicroPython on the ESP32 to run the script.

---

## Usage 🚀

### Run the Project 🏁

1. **Set up the hardware**: Connect the IR sensors, ultrasonic sensor, servo motor, and LCD to the ESP32 according to the configuration in `main.py`.

2. **Upload the code**: Use the MicroPython environment to upload the code to your ESP32.

3. **Configure Telegram bot**: 
   - Set up the bot token and chat ID in `group4secrets.py`.

4. **Access Web Dashboard**: 
   - Once the ESP32 is connected to the network, access the dashboard via your browser by entering the ESP32's IP address.

5. **Test the System**: 
   - Use the ultrasonic sensor to simulate vehicle entry and IR sensors to track car occupancy.

---

## Notes 📝

- The code for the web dashboard is still to be included.
- The Telegram bot functionality will send notifications for each car's exit, including duration and parking fee.
- This repo is a work in progress. Feel free to contribute or submit pull requests!

---

### Videos 🎥

Click on the images below to watch the videos:

[![Smart Parking System Demo - Video 1](https://img.youtube.com/vi/xV_wtUJtxEM/0.jpg)](https://youtu.be/xV_wtUJtxEM?si=tV8HtNeen_QDpBuN)

[![Smart Parking System Demo - Video 2](https://img.youtube.com/vi/rc3CEu1uv04/0.jpg)](https://youtu.be/rc3CEu1uv04?feature=shared)

---

