import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

TELEGRAM_TOKEN = "8538133472:AAFzQrzw2eNETF3CaYNCQ0NmRmvvCGiEwzU"
GEMINI_KEY = "AQ.Ab8RN6JlhYj7eaSkbYcs_7S-V4M..." # حط المفتاح الكامل اللي نسخته من Google هنا
SECRET = "182177"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route(f"/webhook?secret={SECRET}", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data['message']['chat']['id']
    
    if 'text' in data['message']:
        if data['message']['text'] == '/start':
            send_message(chat_id, "حياك في صقر الفلاح الذكي 🌾\nارسل لي صورة نباتك واعطيك التشخيص")
        else:
            send_message(chat_id, "ارسل صورة النبات عشان اشخصه لك")
            
    if 'photo' in data['message']:
        send_message(chat_id, "استلمت الصورة... جاري التحليل 🔍")
        file_id = data['message']['photo'][-1]['file_id']
        file_info = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        img_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        img_data = requests.get(img_url).content
        
        prompt = "أنت خبير زراعي اسمه صقر الفلاح. شخص المرض في هذه الصورة. اعطني: 1. اسم المرض 2. السبب 3. العلاج بخطوات بسيطة 4. طرق الوقاية. جاوب باللهجة السعودية."
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_data}])
        send_message(chat_id, response.text)
        
    return "ok"

@app.route("/")
def home():
    return "Saqr AlFalah Bot is running"
