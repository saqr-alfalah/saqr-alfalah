import os
import telebot
from telebot import types

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🦅 مرحبا بك في بوت صقر الفلاح\nأرسل لي صورة المخالفة أو وصفها وأنا أحللها لك")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    bot.reply_to(message, "📸 استلمت الصورة. جاري التحليل...\n\n⚠️ نوع المخالفة: عدم لبس خوذة السلامة\n📍 المعيار: SA-S-002\n💡 التوصية: إيقاف العمل فورا وتوجيه العامل")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "📝 استلمت وصفك. جاري التحليل...\n\n⚠️ نوع المخالفة: منطقة عمل غير محمية\n📍 المعيار: SA-S-015\n💡 التوصية: وضع حواجز ولوحات تحذيرية")

if __name__ == "__main__":
    print("Bot started...")
    bot.infinity_polling()
