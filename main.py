import os
import google.generativeai as genai
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SECRET = os.environ.get('SECRET', 'default_secret')

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

SF_SYSTEM_PROMPT = """
أنت "ناظر"، خبير أول في منصة "SF GeoAI" للذكاء الجيومكاني الإنشائي. مهمتك تحليل صور وفيديوهات مواقع الإنشاءات وتقديم تقارير فنية فورية.
قواعدك:
1. تحليل الصور: اكتشف المخالفات الفنية مثل شروخ الخرسانة، تعشيش، صدأ الحديد، مخاطر السلامة.
2. الرد بصيغة تقرير: ابدأ بـ *📋 تقرير ناظر الميداني* ثم استخدم **عناوين** واضحة.
3. لا تخترع: اذا الصورة غير واضحة اطلب صورة أوضح.
4. السلامة أولاً: اذا فيه خطر انهيار ابدأ بـ *🚨 تحذير سلامة فوري*
5. رسالة /start: رحب بالمستخدم وعرفه بالمنصة.
6. للأسئلة العامة: جاوب كخبير في البناء والمساحة بالسعودية.
"""

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def analyze_image(image_bytes, user_caption=""):
    image_part = {"mime_type": "image/jpeg", "data": image_bytes}
    prompt_parts = [SF_SYSTEM_PROMPT, "\nحلل هذه الصورة من موقع الإنشاء:", image_part]
    if user_caption:
        prompt_parts.append(f"\nملاحظة من المهندس: {user_caption}")
    response = model.generate_content(prompt_parts)
    return response.text

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.args.get('secret') != SECRET:
        return "Unauthorized", 403
    
    update = request.json
    if 'message' not in update:
        return "ok", 200

    chat_id = update['message']['chat']['id']
    
    if 'text' in update['message']:
        text = update['message']['text']
        if text == '/start':
            welcome_msg = """*أهلاً بك في منصة ناظر 🏗️*
*المنصة الذكية لمتابعة مشاريع الإنشاءات والبنية التحتية.*

*وش أقدر أسوي لك؟*
1. *ارسل صورة للموقع* → أكشف لك المخالفات الفنية لحظياً.
2. *اسألني أي سؤال هندسي* → عن التكاليف، الكميات، كود البناء السعودي.

*مثال: ارسل صورة لعمود خرساني واكتب "شيك على التعشيش"*"""
            send_telegram_message(chat_id, welcome_msg)
        else:
            prompt = f"{SF_SYSTEM_PROMPT}\n\nسؤال المستخدم: {text}"
            response = model.generate_content(prompt)
            send_telegram_message(chat_id, response.text)
            
    elif 'photo' in update['message']:
        file_id = update['message']['photo'][-1]['file_id']
        file_info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        file_info = requests.get(file_info_url).json()
        file_path = file_info['result']['file_path']
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        image_bytes = requests.get(image_url).content
        
        caption = update['message'].get('caption', '')
        send_telegram_message(chat_id, "*📡 جاري تحليل الصورة من قبل ناظر...*")
        analysis_result = analyze_image(image_bytes, caption)
        send_telegram_message(chat_id, analysis_result)

    return "ok", 200

@app.route('/')
def home():
    return "Nather Bot is Running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
