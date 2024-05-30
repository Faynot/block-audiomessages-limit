import time
import telebot
from telebot import types
from datetime import datetime, timedelta
import threading

API_TOKEN = 'YOURE_BOT_TOKEN'
TARGET_USERNAME = 'NAME_FOR_BLOCK_VOICE_MESSAGES'
MAX_SECONDS = 15

bot = telebot.TeleBot(API_TOKEN)

user_voice_durations = {}
lock = threading.Lock()

def reset_durations():
    global user_voice_durations
    while True:
        with lock:
            user_voice_durations = {}
        time.sleep(3600)
        print("Hour left")

reset_thread = threading.Thread(target=reset_durations)
reset_thread.daemon = True
reset_thread.start()
print("Бот запущен")
def mute_user(chat_id, user_id, mute_duration=10):
    until_date = datetime.now() + timedelta(seconds=mute_duration)
    bot.restrict_chat_member(
        chat_id,
        user_id,
        until_date=until_date,
        can_send_messages=True,
        can_send_media_messages=False,
        can_send_other_messages=False,
        can_add_web_page_previews=True
    )
    print("User unmute")

@bot.message_handler(content_types=['voice', 'video_note'])
def handle_voice_and_video_note_messages(message):
    if message.chat.type in ['private', 'group', 'supergroup']:
        if message.from_user.username == TARGET_USERNAME:
            user_id = message.from_user.id
            duration = 0

            if message.voice:
                duration = message.voice.duration
            elif message.video_note:
                duration = message.video_note.duration

            with lock:
                total_duration = user_voice_durations.get(user_id, 0) + duration

                if total_duration > MAX_SECONDS:
                    text = "Sorry, limit."
                    bot.reply_to(message, text)
                    bot.delete_message(message.chat.id, message.message_id)
                    mute_user(message.chat.id, user_id)
                    print("Voice message is licvidate")
                else:
                    user_voice_durations[user_id] = total_duration

if __name__ == '__main__':
    bot.polling(none_stop=True)