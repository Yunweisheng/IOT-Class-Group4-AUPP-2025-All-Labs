try:
    import usocket as socket
except:
    import socket
import network, time, gc, machine
from machine import Pin, I2C
import dht
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

gc.collect()

# ---------- CONFIG ----------
SSID = 'Robotic WIFI'
PASSWORD = 'rbtWIFI@2025'

# ---------- PINS ----------
LED_PIN   = 2      # D2
DHT_PIN   = 4      # D4
TRIG_PIN  = 27     # D27
ECHO_PIN  = 26     # D26
I2C_SDA   = 21     # D21
I2C_SCL   = 22     # D22

# ---------- HW INIT ----------
led = Pin(LED_PIN, Pin.OUT)
dht_sensor = dht.DHT22(Pin(DHT_PIN))
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# LCD init
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400000)
addrs = i2c.scan()
lcd_addr = addrs[0] if addrs else 0x27
lcd = I2cLcd(i2c, lcd_addr, 2, 16)

# ---------- WIFI ----------
def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("WiFi timeout, retry...")
                wlan.disconnect()
                wlan.connect(ssid, password)
                start = time.time()
            time.sleep(0.2)
    print("Connected, ifconfig:", wlan.ifconfig())
    return wlan.ifconfig()[0]

ip = connect_wifi(SSID, PASSWORD)

# ---------- SENSOR HELPERS ----------
def read_dht(retries=3):
    for _ in range(retries):
        try:
            dht_sensor.measure()
            t = dht_sensor.temperature()
            h = dht_sensor.humidity()
            if t is None or h is None:
                raise Exception("DHT returned None")
            return t, h
        except:
            time.sleep(1)
    return None, None

def read_distance(timeout_us=30000):
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    try:
        pulse = machine.time_pulse_us(echo, 1, timeout_us)
        if pulse <= 0:
            return None
        return pulse / 58.0  # µs → cm
    except:
        return None

# ---------- LCD DISPLAY ----------
def lcd_display(dist=None, temp=None):
    lcd.clear()
    lcd.move_to(0, 0)
    if dist is not None:
        lcd.putstr("Dist:{:.1f}cm".format(dist))
    else:
        lcd.putstr("Dist:N/A")
    lcd.move_to(0, 1)
    if temp is not None:
        lcd.putstr("Temp:{:.1f}C".format(temp))
    else:
        lcd.putstr("Temp:N/A")
# ---------- HTML ----------
def webpage(temp, hum, dist, led_state):
    t_str = f"{temp:.1f}" if temp is not None else "N/A"
    h_str = f"{hum:.1f}" if hum is not None else "N/A"
    d_str = f"{dist:.1f}" if dist is not None else "N/A"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ESP32 IoT Webserver</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="10">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background: #f4f7fb;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
    header {{
      background: #0066cc;
      color: white;
      width: 100%;
      text-align: center;
      padding: 20px 0;
      font-size: 1.5em;
      font-weight: bold;
      box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }}
    .container {{
      width: 95%;
      max-width: 700px;
      margin: 20px auto;
    }}
    .card {{
      background: #fff;
      padding: 20px;
      margin: 15px 0;
      border-radius: 12px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .card h2 {{
      margin-top: 0;
      color: #222;
    }}
    .card p {{
      font-size: 1.1em;
      margin: 8px 0;
      color: #333;
    }}
    .btn {{
      display: inline-block;
      padding: 12px 20px;
      margin: 6px 5px;
      border-radius: 6px;
      background: #0078d7;
      color: white;
      font-size: 1em;
      text-decoration: none;
      transition: 0.3s;
    }}
    .btn:hover {{
      background: #005fa3;
    }}
    form input[type=text] {{
      padding: 10px;
      width: 80%;
      max-width: 300px;
      margin: 10px 0;
      border: 1px solid #ccc;
      border-radius: 6px;
    }}
    form input[type=submit] {{
      padding: 10px 20px;
      background: #28a745;
      border: none;
      border-radius: 6px;
      color: white;
      font-size: 1em;
      cursor: pointer;
      transition: 0.3s;
    }}
    form input[type=submit]:hover {{
      background: #1f7a33;
    }}
    footer {{
      margin: 15px 0;
      font-size: 0.85em;
      color: #666;
    }}
  </style>
</head>
<body>
  <header>🌐 ESP32 IoT Webserver</header>
  <div class="container">

    <div class="card">
      <h2>💡 LED Control</h2>
      <p>Status: <b>{led_state}</b></p>
      <a href="/led_on" class="btn">Turn ON</a>
      <a href="/led_off" class="btn">Turn OFF</a>
    </div>

    <div class="card">
      <h2>📊 Sensor Readings</h2>
      <p>🌡 Temperature: <b>{t_str}&deg;C</b></p>
      <p>💧 Humidity: <b>{h_str}%</b></p>
      <p>📏 Distance: <b>{d_str} cm</b></p>
    </div>

    <div class="card">
      <h2>🖥 LCD Controls</h2>
      <a href="/show_dist" class="btn">Show Distance</a>
      <a href="/show_temp" class="btn">Show Temp</a>
      <a href="/show_both" class="btn">Show Both</a>
    </div>

    <div class="card">
      <h2>✍️ Custom LCD Message</h2>
      <form action="/send_text">
        <input type="text" name="msg" placeholder="Enter text for LCD">
        <br>
        <input type="submit" value="Send">
      </form>
    </div>

    <footer>🔄 Page auto-refreshes every 10s</footer>
  </div>
</body>
</html>
"""

# ---------- SERVER ----------
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)
print("Listening on", addr)

def urldecode(s):
    import ure
    s = s.replace('+', ' ')
    hex_pattern = ure.compile(r'%([0-9A-Fa-f]{2})')
    return hex_pattern.sub(lambda m: chr(int(m.group(1), 16)), s)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(2048).decode('utf-8', 'ignore')

        # LED control
        if '/led_on' in request:
            led.value(1)
        elif '/led_off' in request:
            led.value(0)

        # Read sensors
        t, h = read_dht()
        d = read_distance()
        led_state = "ON" if led.value() else "OFF"
        # LCD actions
        if '/show_dist' in request:
            lcd_display(dist=d, temp=None)
        elif '/show_temp' in request:
            lcd_display(dist=None, temp=t)
        elif '/show_both' in request:
            lcd_display(dist=d, temp=t)

        # Custom LCD text
        if '/send_text' in request:
            try:
                line = request.split('\n')[0]
                path = line.split(' ')[1]
                if '?' in path:
                    qs = path.split('?', 1)[1]
                    if 'msg=' in qs:
                        val = qs.split('msg=', 1)[1].split('&')[0]
                        val = urldecode(val)
                        lcd.clear()
                        if len(val) <= 16:
                            lcd.putstr(val)
                        else:
                            lcd.putstr(val[:16])
                            lcd.move_to(0, 1)
                            lcd.putstr(val[16:32])
            except Exception as e:
                print("Custom text error:", e)

        # Send webpage
        response = webpage(t, h, d, led_state)
        header = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n"
        conn.send(header.encode('utf-8'))
        conn.send(response.encode('utf-8'))
        conn.close()

    except Exception as e:
        print("Server error:", e)
        try:
            conn.close()
        except:
            pass
        time.sleep(0.1)