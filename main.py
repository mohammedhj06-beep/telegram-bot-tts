import telebot
import asyncio
import edge_tts
import os

TOKEN = "8700870404:AAGeXeKHrSF9G87VFvGyWN9ICvdD977Pf1c"
CHANNEL = "@lio8l1"

bot = telebot.TeleBot(TOKEN)
user_settings = {}

VOICES = {
    "male_ar": "ar-SA-HamedNeural",
    "female_ar": "ar-SA-ZariyahNeural",
    "male_en": "en-US-GuyNeural",
    "female_en": "en-US-JennyNeural"
}

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

def force_sub(message):
    bot.send_message(
        message.chat.id,
        f"لاستخدام البوت، اشترك أولاً في القناة:\n{CHANNEL}"
    )

@bot.message_handler(commands=['start'])
def start(message):
    if not is_subscribed(message.from_user.id):
        force_sub(message)
        return

    bot.send_message(
        message.chat.id,
        "👋 أهلاً! أرسل النص وسيتم تحويله إلى صوت."
    )

@bot.message_handler(func=lambda m: True)
def tts_handler(message):
    if not is_subscribed(message.from_user.id):
        force_sub(message)
        return

    if message.text.startswith("/"):
        return

    voice = user_settings.get(message.from_user.id, "female_ar")
    filename = f"{message.from_user.id}.mp3"

    async def generate():
        communicate = edge_tts.Communicate(message.text, VOICES[voice])
        await communicate.save(filename)

    try:
        asyncio.run(generate())
        with open(filename, "rb") as audio:
            bot.send_voice(message.chat.id, audio)
        os.remove(filename)
    except:
        bot.send_message(message.chat.id, "❌ خطأ في التحويل.")

bot.infinity_polling()
