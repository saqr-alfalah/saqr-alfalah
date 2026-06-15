from flask import Flask, request
import telebot
import os

TOKEN = "8538133472:AAFzQrzw2eNETF3CaYNCQ0NmRmvvCGiEwzU"
SECRET = "182177"

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

@app.route('/')
def home():
    return 'Bot is running'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.args.get('secret')!= SECRET:
        return 'Unauthorized', 403
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "حياك الله في بوت صقر الفلاح 🌾")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "وصلتني: " + message.text)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
