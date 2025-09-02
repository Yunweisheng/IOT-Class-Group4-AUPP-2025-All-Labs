import network, time, urequests
from machine import Pin, reset
import dht

# =======================
# CONFIG
# =======================
WIFI_SSID     = "Robotic WIFI"
WIFI_PASSWORD = "rbtWIFI@2025"

BOT_TOKEN     = "8239071008:AAE7sZfmDBJ_4rKoxrV_oxGukAqObOmLWj8"
# Include your private chats and group IDs (negative numbers are groups)
CHAT_IDS      = [1032247155, 1039563806, -4985603296, 741464258]

API = "https://api.telegram.org/bot" + BOT_TOKEN

RELAY_PIN        = 5        # GPIO5
RELAY_ACTIVE_LOW = False    # set True if relay works inverted
DEBUG            = True

# Telegram long-poll timeout (smaller = more responsive)
POLL_TIMEOUT_S   = 1

# DHT config
DHT_PIN          = 4        # GPIO4 for DHT
SENSOR_TYPE      = "DHT22"  # set "DHT11" if using DHT11

# Temperature logic
TEMP_THRESHOLD_C          = 30.0  # "hot" if strictly above this
TEMP_CHECK_INTERVAL_S     = 5     # read sensor every 5s (matches alert cadence)
NOTIFY_COOLDOWN_S         = 300   # 5 min cooldown when relay is ON & hot
ALERT_WHEN_OFF_INTERVAL_S = 5     # when relay OFF & hot, alert every 5s

# =======================
# STATE
# =======================
relay = Pin(RELAY_PIN, Pin.OUT)
_sensor = None

# Auto-off behavior: armed when /on while hot; turns off when temp <= threshold
auto_off_pending = False

# Notification state
last_temp_sent_ts = 0
last_hot_state = False     # last known "hot" state
last_temp = None
last_hum = None

# For 5s alert mode (relay OFF & hot)
last_off_alert_ts = 0

# Timing helpers
def _now_s():
    return time.ticks_ms() // 1000

def _elapsed_s(start_s):
    return (_now_s() - start_s) & 0x7FFFFFFF

# =======================
# HELPERS
# =======================
def _urlencode(d):
    parts = []
    for k, v in d.items():
        if isinstance(v, (int, float)):
            v = str(v)
        s = str(v)
        s = s.replace("%", "%25").replace(" ", "%20").replace("\n", "%0A")
        s = s.replace("&", "%26").replace("?", "%3F").replace("=", "%3D")
        parts.append(str(k) + "=" + s)
    return "&".join(parts)

def log(*args):
    if DEBUG:
        print(*args)

# ---- relay control ----
def relay_on():
    relay.value(0 if RELAY_ACTIVE_LOW else 1)
    log("Relay turned ON")

def relay_off():
    relay.value(1 if RELAY_ACTIVE_LOW else 0)
    log("Relay turned OFF")

def relay_is_on():
    return (relay.value() == 0) if RELAY_ACTIVE_LOW else (relay.value() == 1)

# ---- DHT reader ----
def _init_sensor():
    global _sensor
    if _sensor is None:
        if SENSOR_TYPE.upper() == "DHT22":
            _sensor = dht.DHT22(Pin(DHT_PIN))
        else:
            _sensor = dht.DHT11(Pin(DHT_PIN))
    return _sensor

def temp_reader():
    global last_temp, last_hum
    try:
        sensor = _init_sensor()
        sensor.measure()
        # Keep this short for responsiveness; bump to 0.2–0.5 if your sensor is fussy
        time.sleep(0.15)
        t = sensor.temperature()
        h = sensor.humidity()
        last_temp, last_hum = t, h
        log("Temperature:", t, "°C, Humidity:", h, "%")
        return t, h
    except OSError as e:
        print("Failed to read sensor:", e)
        return None, None

# ---- Wi-Fi ----
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # Optional: try to reduce latency if your firmware supports it
    try:
        if hasattr(wlan, "config"):
            wlan.config(pm = 0)  # some ports use 'pm' or 'ps_mode'
    except Exception:
        pass

    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        timeout = 25
        while timeout > 0 and not wlan.isconnected():
            timeout -= 1
            time.sleep(1)
            print(".", end="")
        print()
        if not wlan.isconnected():
            raise RuntimeError("Wi-Fi connect timeout")
    print("Wi-Fi connected:", wlan.ifconfig()[0])
    return wlan

# ---- Telegram API ----
def _http_get(url):
    # Try a short timeout if available; fall back if not supported
    try:
        return urequests.get(url, timeout=3)
    except TypeError:
        return urequests.get(url)

def send_message(chat_id, text):
    try:
        url = API + "/sendMessage?" + _urlencode({"chat_id": chat_id, "text": text})
        log("Sending to:", url[:60] + "...")
        r = _http_get(url)
        r.close()
        return True
    except Exception as e:
        print("send_message error:", e)
        return False

def broadcast(text):
    ok = True
    for cid in CHAT_IDS:
        ok = send_message(cid, text) and ok
    return ok

def get_updates(offset=None, timeout=POLL_TIMEOUT_S):
    qs = {"timeout": timeout}
    if offset is not None:
        qs["offset"] = offset
    url = API + "/getUpdates?" + _urlencode(qs)
    try:
        r = _http_get(url)
        data = r.json()
        r.close()
        if not data.get("ok"):
            print("getUpdates not ok:", data.get("description", "Unknown error"))
            return []
        updates = data.get("result", [])
        return updates
    except Exception as e:
        print("get_updates error:", e)
        return []

# ---- Command handler ----
def _strip_bot_mention(t):
    if not t:
        return t
    if "@" in t:
        return t.split("@", 1)[0]
    return t

def handle_cmd(chat_id, text):
    global auto_off_pending, last_temp, last_hum
    t = (text or "").strip()
    t_lower = _strip_bot_mention(t.lower())
    log(f"Processing command: '{t_lower}' from {chat_id}")

    if t_lower in ("/on", "on"):
        # Fresh read to decide auto-off accurately
        t_now, h_now = temp_reader()
        if t_now is not None:
            last_temp, last_hum = t_now, h_now

        relay_on()
        send_message(chat_id, "✅ Relay: ON")

        if (last_temp is not None) and (last_temp > TEMP_THRESHOLD_C):
            auto_off_pending = True
            send_message(chat_id, "🟠 Auto-off armed: will turn OFF when temperature falls below 30 °C.")
        else:
            auto_off_pending = False

    elif t_lower in ("/off", "off"):
        relay_off()
        auto_off_pending = False
        send_message(chat_id, "❌ Relay: OFF")

    elif t_lower in ("/status", "status"):
        status = "ON" if relay_is_on() else "OFF"
        extra = ""
        if last_temp is not None:
            extra = f"\n🌡️ {last_temp}°C"
        if auto_off_pending:
            extra += "\n⏱️ Auto-off pending (will OFF when ≤ 30 °C)."
        send_message(chat_id, f"📊 Relay status: {status}{extra}")

    elif t_lower in ("/temp", "temp", "/temperature"):
        t2, h2 = temp_reader()
        if t2 is not None:
            send_message(chat_id, f"🌡️ Temperature: {t2}°C\n💧 Humidity: {h2}%")
        else:
            send_message(chat_id, "❌ Failed to read sensor. Check connections.")

    elif t_lower in ("/whoami", "whoami"):
        send_message(chat_id, f"🆔 Your chat ID: {chat_id}")

    elif t_lower in ("/start", "/help", "help"):
        help_text = """🤖 Available commands:
/on - Turn relay ON (if hot, auto-off triggers when it cools)
/off - Turn relay OFF
/status - Check relay & temp status
/temp - Read temperature & humidity
/whoami - Show your chat ID
/help - Show this message

ℹ️ Notes:
• Alerts are sent only when > 30 °C.
• If relay is OFF and it's hot, you'll get alerts every 5 seconds.
• In groups, you can use /on@YourBotName, /off@YourBotName, etc.
• To receive ALL messages in groups, disable bot privacy mode in BotFather."""
        send_message(chat_id, help_text)

    else:
        send_message(chat_id, f"❓ Unknown command: '{text}'\nType /help for available commands")

# ---- Temperature notify logic ----
def maybe_notify_temperature(t, h):
    """
    - If relay OFF & hot: alert every ALERT_WHEN_OFF_INTERVAL_S seconds.
    - If relay ON & hot: one warning, then reminders every NOTIFY_COOLDOWN_S.
    - When cooling to normal (≤ threshold): send 'Back to normal' once.
    """
    global last_temp_sent_ts, last_hot_state, last_off_alert_ts

    if t is None:
        return

    now = _now_s()
    is_hot = t > TEMP_THRESHOLD_C
    is_on = relay_is_on()

    # PRIORITY: relay OFF & hot -> alert every 5s (no cooldown)
    if (not is_on) and is_hot:
        if _elapsed_s(last_off_alert_ts) >= ALERT_WHEN_OFF_INTERVAL_S:
            broadcast(f"🚨 HOT & RELAY OFF: {t}°C (> 30°C).")
            last_off_alert_ts = now
        # mark hot-state so we later send recovery once
        last_hot_state = True
        return

    # General hot behavior
    if is_hot and not last_hot_state:
        broadcast(f"🔥 Warning: {t}°C (> 30°C).")
        last_temp_sent_ts = now
        last_hot_state = True
        return

    if is_hot and last_hot_state:
        # relay could be ON here -> throttle reminders
        if _elapsed_s(last_temp_sent_ts) >= NOTIFY_COOLDOWN_S:
            broadcast(f"🔥 Still hot: {t}°C.")
            last_temp_sent_ts = now
        return

    # Back to normal
    if (not is_hot) and last_hot_state:
        broadcast(f"✅ Back to normal: {t}°C (≤ 30°C).")
        last_hot_state = False
        # reset off-alert timer so next hot-off cycle starts fresh
        last_off_alert_ts = now
        return

# ---- Auto-off processing ----
def maybe_auto_off(t):
    """
    Auto-off: if user turned ON while hot, we armed auto_off_pending.
    When temp drops to ≤ threshold, turn relay OFF and clear the flag.
    """
    global auto_off_pending
    if auto_off_pending and t is not None and t <= TEMP_THRESHOLD_C:
        if relay_is_on():
            relay_off()
            broadcast("⛳ Auto-off: temperature fell ≤ 30 °C. Relay turned OFF.")
        auto_off_pending = False

# ---- Main loop ----
def main():
    global last_temp, last_hum

    print("🚀 Starting Telegram Temperature Bot...")

    # Connect Wi-Fi
    try:
        connect_wifi()
    except Exception as e:
        print("Wi-Fi connection failed:", e)
        time.sleep(10)
        reset()

    # Init relay OFF
    relay_off()
    print("🔌 Relay initialized (OFF)")

    # Skip old updates
    last_id = None
    try:
        old_updates = get_updates(timeout=1)
        if old_updates:
            last_id = old_updates[-1]["update_id"]
            print(f"📨 Skipped {len(old_updates)} old message(s)")
    except:
        pass

    print("✅ Bot is ready! Send commands via Telegram...")

    error_count = 0
    max_errors = 10
    last_sensor_read_s = 0

    while True:
        try:
            # Ensure Wi-Fi
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("🔄 Wi-Fi disconnected, reconnecting...")
                connect_wifi()

            # 1) Poll Telegram (fast)
            updates = get_updates(offset=(last_id + 1) if last_id else None, timeout=POLL_TIMEOUT_S)

            if updates:
                for upd in updates:
                    last_id = upd["update_id"]
                    msg = upd.get("message", {})
                    chat = msg.get("chat", {})
                    chat_id = chat.get("id")
                    text = msg.get("text")
                    user_from = msg.get("from", {})
                    username = user_from.get("username", "Unknown")
                    chat_type = chat.get("type")

                    if not chat_id:
                        continue

                    print(f"📥 @{username} ({chat_type}:{chat_id}): {text}")

                    if chat_id in CHAT_IDS:
                        handle_cmd(chat_id, text)
                    else:
                        send_message(chat_id, f"🚫 Unauthorized access.\nYour chat ID: {chat_id}")
                        print(f"⚠️ Unauthorized access attempt from {chat_id}")

            # 2) Periodic sensor read (matches alert cadence)
            now_s = _now_s()
            if _elapsed_s(last_sensor_read_s) >= TEMP_CHECK_INTERVAL_S:
                t, h = temp_reader()
                last_sensor_read_s = now_s
                if t is not None:
                    maybe_notify_temperature(t, h)
                    maybe_auto_off(t)

            error_count = 0

            # Tiny yield for responsiveness
            time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n👋 Bot stopped by user")
            break

        except Exception as e:
            error_count += 1
            print(f"❌ Error #{error_count}: {e}")

            if error_count >= max_errors:
                print(f"💀 Too many errors ({max_errors}), restarting...")
                time.sleep(5)
                reset()
            else:
                time.sleep(2)

# ---- Entry point ----
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("💥 Fatal error:", e)
        print("🔄 Restarting in 10 seconds...")
        time.sleep(10)
        reset()
