import os
import google.generativeai as genai
from flask import Flask, request
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SECRET = os.environ.get('SECRET', '182177')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route(f"/webhook?secret={SECRET}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        if text == "/start":
            reply = "أهلاً بك! أنا صقر الفلاح 🌾\nأساعدك في استشارات زراعية فورية. أرسل لي سؤالك أو صورة للنبات."
        else:
            response = model.generate_content(f"أنت خبير زراعي اسمه صقر الفلاح. جاوب باختصار على: {text}")
            reply = response.text
        send_message(chat_id, reply)
    return "ok"

@app.route("/")
def home():
    return "Saqr AlFalah Bot is running"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
