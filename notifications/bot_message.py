import requests
from django.conf import settings

TOKEN = settings.TELEGRAM_BOT_TOKEN

CHAT_ID = settings.CHAT_ID

def send_message(text):


    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={"chat_id": CHAT_ID, "text": text})
