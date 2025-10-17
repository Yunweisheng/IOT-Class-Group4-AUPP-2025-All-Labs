# ==========================================================
# group4main.py — Smart Parking System (3 Slots) + Web Dashboard
# Hardened against OSError:23 socket bind errors
# ==========================================================
import machine
import sys
import gc
from machine import Pin, PWM, SoftI2C, time_pulse_us, reset
from time import sleep, sleep_us, time, localtime, ticks_ms, ticks_diff
import network, _thread
import group4telegram_bot as telegram_bot
import group4secrets as secrets
import group4i2c_lcd as lcd_driver
import Web_DashboardGroup4 as web_dashboard
import usocket as socket  # low-level socket for cleanup

# ---------------- CONFIG ----------------
IR_PINS = (32, 33, 34)
TRIG_PIN, ECHO_PIN = 27, 26
SERVO_PIN = 16
I2C_SDA, I2C_SCL = 21, 22
LCD_ADDR, LCD_W, LCD_H = 0x27, 16, 2

ENTRY_DISTANCE_CM = 15
FEE_PER_MIN = 0.5
SERVO_CLOSE_US, SERVO_OPEN_US = 1100, 1900
LCD_REFRESH_MS, EXIT_GRACE_MS = 500, 1000

# ---------------- STATE ----------------
slots = {3: {"occupied": False, "id": None, "time_in": None, "time_out": None, "free_since": None}, 
         1: {"occupied": False, "id": None, "time_in": None, "time_out": None, "free_since": None}, 
         2: {"occupied": False, "id": None, "time_in": None, "time_out": None, "free_since": None}}

closed_tickets = []
_available_ids = set(range(1, 4))
web_dashboard.slots = slots
web_dashboard.closed_tickets = closed_tickets

# ---------------- HW globals ----------------
_lcd = None
_lcd_enabled = False
_last_lcd_update = 0
servo = None
_gate_open = False

# ---------------- UTIL: cleanup & network reset ----------------
def cleanup_sockets_once():
    """Attempt to free any leftover sockets and run GC."""
    try:
        s = socket.socket()
        s.close()
        print("✅ Socket cleanup successful")
    except Exception as e:
        print(f"⚠️ Socket cleanup failed: {e}")
    gc.collect()
    print(f"🧠 Free memory: {gc.mem_free()} bytes")


def reset_wifi_interface():
    """Hard-reset the STA interface to clear OS-level state."""
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        sleep(1)
        gc.collect()
        wlan.active(True)
        sleep(1)
        print("✅ Wi-Fi interface reset")
    except Exception as e:
        print(f"⚠️ Wi-Fi reset failed: {e}")
    gc.collect()

# ---------------- LCD ----------------
def _lcd_init():
    global _lcd, _lcd_enabled
    try:
        i2c = SoftI2C(sda=Pin(I2C_SDA), scl=Pin(I2C_SCL))
        scan = i2c.scan()
        if not scan:
            raise Exception("no I2C devices found")
        addr = LCD_ADDR if LCD_ADDR in scan else scan[0]
        _lcd = lcd_driver.I2cLcd(i2c, addr, LCD_H, LCD_W)
        _lcd.clear(); _lcd.putstr("Smart Parking")
        _lcd_enabled = True
        print("✅ LCD initialized")
    except Exception as e:
        print(f"❌ LCD init failed: {e}")
        _lcd_enabled = False


def _lcd_show(line1, line2=""):
    if not _lcd_enabled:
        return
    try:
        _lcd.clear()
        _lcd.move_to(0, 0); _lcd.putstr(line1[:LCD_W])
        _lcd.move_to(0, 1); _lcd.putstr(line2[:LCD_W])
    except Exception as e:
        print(f"⚠️ LCD error: {e}")

# ---------------- WIFI ----------------
def connect_wifi(timeout=15):
    reset_wifi_interface()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
    print("Connecting to Wi-Fi...")
    start = time()
    while not wlan.isconnected() and (time() - start) < timeout:
        sleep(1)
        print("Trying to connect to Wi-Fi...")
    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
        print("Wi-Fi connected! IP:", ip)
        return ip
    print("❌ Wi-Fi failed to connect")
    return None

# ---------------- SENSORS ----------------
_ir = []
TRIG, ECHO = None, None

def init_sensors():
    global _ir, TRIG, ECHO
    _ir = [Pin(p, Pin.IN, Pin.PULL_UP) for p in IR_PINS]
    TRIG = Pin(TRIG_PIN, Pin.OUT); ECHO = Pin(ECHO_PIN, Pin.IN)
    TRIG.off()
    print("✅ Sensors ready")

def distance_cm():
    TRIG.off(); sleep_us(2)
    TRIG.on(); sleep_us(10)
    TRIG.off()
    t = time_pulse_us(ECHO, 1, 30000)
    if t < 0:
        return None
    return (t * 0.0343) / 2

# ---------------- SERVO ----------------
def _us_to_duty_u16(pulse_us, freq=50):
    period = 1_000_000 // freq
    return int(min(max((pulse_us * 65535) // period, 0), 65535))

def init_servo():
    global servo
    servo = PWM(Pin(SERVO_PIN))
    servo.freq(50)
    print("✅ Servo attached")

def gate_open():
    global _gate_open
    if sum(1 for s in slots.values() if not s["occupied"]) > 0:
        servo.duty_u16(_us_to_duty_u16(SERVO_OPEN_US))
        _gate_open = True
        print("🚗 Gate opened")

def gate_close():
    global _gate_open
    servo.duty_u16(_us_to_duty_u16(SERVO_CLOSE_US))
    _gate_open = False
    print("🚧 Gate closed")

# ---------------- PARKING LOGIC ----------------
def now_hms(t=None):
    if not t:
        t = time()
    lt = localtime(t)
    return "{:02d}:{:02d}:{:02d}".format(lt[3], lt[4], lt[5])

def assign_id(slot):
    tid = min(_available_ids)
    _available_ids.remove(tid)
    slots[slot].update(occupied=True, id=tid, time_in=time(), free_since=None)
    web_dashboard.broadcast_event(f"🚗 Car entered Slot S{slot}")
    _lcd_show(f"Car IN: S{slot}", "Updating...")
    print(f"🎫 OPEN | Slot {slot} | ID {tid} | {now_hms()}")

def handle_exit(slot):
    s = slots[slot]; tid = s["id"]; t_out = time()
    duration = max(1, (t_out - s["time_in"]) // 60)
    fee = duration * FEE_PER_MIN
    closed_tickets.append({"id": tid, "slot": slot, "duration": f"{duration} min", "fee": fee, "time_out": now_hms(t_out)})
    web_dashboard.broadcast_event(f"⬆️ Car exited Slot S{slot} — now FREE")
    _lcd_show(f"Car OUT: S{slot}", f"Fee ${fee:.2f}")
    print(f"✅ CLOSE | Slot {slot} | ID {tid} | Fee ${fee:.2f}")
    try:
        telegram_bot.send_ticket(tid, slot, duration, fee, now_hms(s["time_in"]), now_hms(t_out))
    except Exception as e:
        print(f"⚠️ Telegram send error: {e}")
    _available_ids.add(tid)
    s.update(occupied=False, id=None, time_in=None, time_out=None, free_since=None)

def lcd_update():
    global _last_lcd_update
    now = ticks_ms()
    if ticks_diff(now, _last_lcd_update) < LCD_REFRESH_MS:
        return
    free_slots = [f"S{i}" for i, s in slots.items() if not s["occupied"]]
    line1 = "Free: " + (" ".join(free_slots) if free_slots else "FULL")
    line2 = "Gate: " + ("Open" if _gate_open else "Closed")
    _lcd_show(line1, line2)
    _last_lcd_update = now

# ---------------- DASHBOARD START (robust) ----------------
def start_dashboard_with_retries(max_attempts=4, wait_s=10):
    ports = [8080, 8000, 8888]
    for port in ports:
        print(f"🌐 Trying dashboard on port {port}...")
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"🌐 Web Dashboard start attempt {attempt}/{max_attempts} on port {port}...")
                web_dashboard.start_server(port=port)
                return True
            except Exception as e:
                print(f"⚠️ Dashboard start failed on port {port}: {e}")
                cleanup_sockets_once()
                reset_wifi_interface()
                gc.collect()
                if attempt < max_attempts:
                    print(f"⏳ Waiting {wait_s}s before retrying...")
                    sleep(wait_s)
                else:
                    print(f"❌ Could not start dashboard on port {port} — trying next port...")
    print("❌ Dashboard could not start on any port — continuing without dashboard.")
    return False

# ---------------- MAIN LOOP ----------------
def sensors_loop():
    print("🚀 Sensors loop running in background thread")
    detect_hits = miss_hits = 0
    while True:
        try:
            gc.collect()
            dist = distance_cm() or 999
            if dist < ENTRY_DISTANCE_CM:
                detect_hits += 1
                miss_hits = 0
            else:
                miss_hits += 1
                detect_hits = 0

            # Open the gate when a car is detected
            if detect_hits >= 3 and not _gate_open: 
                gate_open()
            if miss_hits >= 10 and _gate_open: 
                gate_close()

            # Check the IR sensor states for each parking slot (1, 2, 3)
            for i, pin in enumerate(_ir, 1): 
                car = (pin.value() == 0)  # Car is detected when the sensor reads LOW
                s = slots[i]  # Access the specific slot
                if car and not s["occupied"]:  # If the car enters an empty slot
                    assign_id(i)  # Assign car to the slot
                elif not car and s["occupied"]:  # If the car leaves an occupied slot
                    if s["free_since"] is None:
                        s["free_since"] = ticks_ms()
                    elif ticks_diff(ticks_ms(), s["free_since"]) >= EXIT_GRACE_MS:  # Grace period to confirm exit
                        handle_exit(i)  # Handle the exit and billing

            lcd_update()  # Update the LCD with the current slot status
            sleep(0.1)  # Small delay for sensor updates
        except Exception as e:
            print(f"⚠️ Sensors loop error: {e}")
            sleep(0.5)

# ---------------- STARTUP ----------------
if __name__ == "__main__":
    print("\nSMART PARKING SYSTEM — v4.0\n")
    cleanup_sockets_once()

    print("[1/4] Wi-Fi…")
    ip = connect_wifi()
    if not ip:
        print("⚠️ System will run without Wi-Fi/Telegram")

    print("[2/4] Telegram…")
    try:
        telegram_bot.set_config(secrets.BOT_TOKEN, secrets.GROUP_CHAT_ID)
        telegram_bot.test_telegram()
    except Exception as e:
        print(f"⚠️ Telegram init error: {e}")
        print("ℹ️ Continuing without Telegram")

    print("[3/4] LCD…"); _lcd_init()
    print("[4/4] Sensors…"); init_sensors()
    print("[5/5] Servo…"); init_servo(); sleep(0.5); gate_close()

    print(f"✅ System ready! Open dashboard at http://{ip if ip else 'ESP32-IP'}:8080 (or 8000, 8888)")
    print(f"🧠 Free memory: {gc.mem_free()} bytes")

    _thread.start_new_thread(sensors_loop, ())
    start_dashboard_with_retries()

