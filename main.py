import telebot
import asyncio
import edge_tts
import os

TOKEN = os.getenv("TOKEN")
CHANNEL = "@lio8l1"

bot = telebot.TeleBot(TOKEN)

VOICES = {
    "ar": "ar-SA-HamedNeural",
    "en": "en-US-GuyNeural",
    "jp": "ja-JP-NanamiNeural"
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
        f"🚫 اشترك أولًا في القناة:\n{CHANNEL}"
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

@bot.message_handler(commands=['lang'])
def change_lang(message):
    bot.send_message(
        message.chat.id,
        "🌍 اختر اللغة:\n/ar - عربي\n/en - English\n/jp - 日本語"
    )

@bot.message_handler(func=lambda m: m.text in ["/ar", "/en", "/jp"])
def set_lang(message):
    bot.user_lang = message.text[1:]
    bot.send_message(message.chat.id, f"✅ تم اختيار: {bot.user_lang}")

@bot.message_handler(func=lambda m: True)
def tts(message):
    if not is_subscribed(message.from_user.id):
        force_sub(message)
        return

    text = message.text
    if not text:
        return

    lang = getattr(bot, "user_lang", "ar")
    voice = VOICES.get(lang, VOICES["ar"])

    filename = f"{message.from_user.id}.mp3"

    async def generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

    try:
        asyncio.run(generate())
        with open(filename, "rb") as audio:
            bot.send_voice(message.chat.id, audio)
    except:
        bot.send_message(message.chat.id, "❌ خطأ في التحويل")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

bot.polling()
