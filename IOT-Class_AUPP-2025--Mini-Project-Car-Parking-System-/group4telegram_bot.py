try:
    import urequests as requests
except ImportError:
    import requests
import _thread
import gc
from time import sleep

BOT_TOKEN = None
GROUP_CHAT = None
API_BASE = None
telegram_queue = []  # Queue to store messages before sending

# Flag to track if the bot is initialized
is_bot_initialized = False

# Initialize the bot configuration
def set_config(bot_token, group_chat_id):
    global BOT_TOKEN, GROUP_CHAT, API_BASE, is_bot_initialized
    BOT_TOKEN = bot_token
    GROUP_CHAT = group_chat_id
    API_BASE = f"https://api.telegram.org/bot{BOT_TOKEN}"
    is_bot_initialized = True  # Mark the bot as initialized
    print(f"🤖 Telegram configured | Group ID: {GROUP_CHAT}")
    _thread.start_new_thread(telegram_worker, ())  # Start worker thread for sending messages

# URL encoding for special characters (e.g., spaces, newlines)
def url_encode(text):
    text = str(text).replace("✅", "%E2%9C%85").replace("\n", "%0A").replace(" ", "%20")
    return text

# Send a message to Telegram chat
def send_message(chat_id, text):
    if not is_bot_initialized:
        print("❌ Telegram Bot not initialized!")
        return False
    
    if not API_BASE:
        return False
    
    res = None
    try:
        url = f"{API_BASE}/sendMessage?chat_id={chat_id}&text={url_encode(text)}"
        print("DEBUG: Sending URL:", url)
        gc.collect()
        res = requests.get(url, timeout=10)  # Sending the request
        print("DEBUG: Telegram HTTP status:", res.status_code)
        _ = res.text  # Consume the response to close the connection
        print("✅ Telegram sent:", text)
        return True
    except Exception as e:
        print("❌ Telegram error:", e)
        return False
    finally:
        try:
            if res:
                res.close()  # Close the connection
        except Exception:
            pass
        gc.collect()

# Worker thread that processes the telegram queue and sends messages
def telegram_worker():
    while True:
        if telegram_queue:  # Check if there are messages in the queue
            chat_id, msg = telegram_queue.pop(0)  # Get the first message
            send_message(chat_id, msg)  # Send the message
        sleep(1)  # Sleep for a second to prevent high CPU usage

# Send a ticket message to the Telegram group
def send_ticket(ticket_id, slot_num, minutes, fee, time_in=None, time_out=None):
    msg = f"✅ Ticket CLOSED\nID:{ticket_id}\nSlot:S{slot_num}\nDuration:{minutes}min\nFee:${fee:.2f}"
    if time_in and time_out:
        msg += f"\nTime-In:{time_in}\nTime-Out:{time_out}"
    
    # Add the message to the queue for sending
    telegram_queue.append((GROUP_CHAT, msg))

# Test the Telegram bot functionality
def test_telegram():
    if is_bot_initialized:
        telegram_queue.append((GROUP_CHAT, "Test message from ESP32 Smart Parking System"))
    else:
        print("⚠️ Telegram Bot not initialized yet.")

# Notify the Telegram group when parking is full
def notify_full_parking():
    if is_bot_initialized:
        message = "🚧 Parking is FULL! No space available."
        telegram_queue.append((GROUP_CHAT, message))

# Notify the Telegram group when a slot becomes free
def notify_free_slot(slot_num):
    if is_bot_initialized:
        message = f"🚗 Slot S{slot_num} is now FREE!"
        telegram_queue.append((GROUP_CHAT, message))

