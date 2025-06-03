
import requests

BOT_TOKEN = "7976031453:AAFWtIKSt93AQFOvfUtDa0WxeqHS-Vnleyw"
CHAT_ID = "5819357765"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
