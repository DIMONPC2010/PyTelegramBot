import telebot
import openai_request
import random
import os
import psutil

TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
EXPERT_COMMAND = ['expert', 'эксперт']
QUESTION_COMMAND = ['question', 'вопрос']
START_COMMAND = ['start', 'старт']
START_CHAT_COMMAND = ['startchat', 'стартчат']
HELLO_COMMAND = ['hi', 'hello', 'здаров']
CPU_COMMAND = ['cpu']
RAM_COMMAND = ['ram']
DISK_COMMAND = ['disk']

bot = telebot.TeleBot(TELEGRAM_API_KEY)

@bot.message_handler(commands=HELLO_COMMAND)
def send_welcome(message):
    bot.reply_to(message, random.choice(HELLO_COMMAND))

@bot.message_handler(commands=START_COMMAND)
def send_start(message):
    openai_request.reset_private_message_cach(message.from_user.id)

    user_name_result = ""
    if message.from_user.username:
        user_name_result = str(message.from_user.username)
    elif message.from_user.first_name:
        user_name_result = str(message.from_user.first_name)

        if message.from_user.last_name:
            user_name_result += (" " + str(message.from_user.last_name))
    else:
        user_name_result = str(message.from_user.id)

    bot.reply_to(message, "Message cach for user: " + user_name_result + ", deleted.")

@bot.message_handler(commands=START_CHAT_COMMAND)
def send_startchat(message):
    openai_request.reset_public_message_cach(message.chat.id)
    bot.reply_to(message, "Message cach for chat: " + str(message.chat.id) + ", deleted.")

@bot.message_handler(commands=EXPERT_COMMAND)
def send_expertopinion(message):
    response = openai_request.chat_gpt_request(message.text, message.from_user.id, openai_request.QuestionType.private_session)
    bot.reply_to(message, response)

@bot.message_handler(commands=QUESTION_COMMAND)
def send_questionopinion(message):
    response = openai_request.chat_gpt_request(message.text, message.chat.id, openai_request.QuestionType.public_session)
    bot.reply_to(message, response)

@bot.message_handler(commands=CPU_COMMAND)
def send_cpu_usage(message):
    load1, load5, load15 = psutil.getloadavg()

    cpu_usage1 = (load1/os.cpu_count()) * 100
    cpu_usage5 = (load5/os.cpu_count()) * 100
    cpu_usage15 = (load15/os.cpu_count()) * 100
 
    response = f"The CPU usage for last  1m is: {cpu_usage1:.2f}%\n" 
    response += f"The CPU usage for last  5m is: {cpu_usage5:.2f}%\n"
    response += f"The CPU usage for last 15m is: {cpu_usage15:.2f}%"
    bot.reply_to(message, response)

@bot.message_handler(commands=RAM_COMMAND)
def send_ram_usage(message):
    ram_available = psutil.virtual_memory()[1]/1000000
    ram_usage = psutil.virtual_memory()[2]
    ram_used = psutil.virtual_memory()[3]/1000000
 
    response = f"RAM available: {ram_available:.2f} MB\n"
    response += f"RAM used: {ram_used:.2f} MB\n"
    response += f"RAM memory used: {ram_usage}%\n"
    bot.reply_to(message, response)

@bot.message_handler(commands=DISK_COMMAND)
def send_disk_usage(message):
    disk_info = psutil.disk_usage("/")
 
    response = f"Total: {disk_info.total / 1024 / 1024 / 1024:.2f} GB\n"
    response += f"Used: {disk_info.used / 1024 / 1024 / 1024:.2f} GB\n"
    response += f"Free: {disk_info.free / 1024 / 1024 / 1024:.2f} GB"
    bot.reply_to(message, response)

@bot.message_handler(content_types=["text"])
def send_reply_to_message(message):
    if message.reply_to_message:
        if message.reply_to_message.from_user:
            if message.reply_to_message.from_user.username:
                if bot.get_me().username == message.reply_to_message.from_user.username:
                    response = openai_request.chat_gpt_request(message.text, message.chat.id, openai_request.QuestionType.public_session)
                    bot.reply_to(message, response)
    else:
        if f'@{bot.get_me().username}' in message.text:
            response = openai_request.chat_gpt_request(message.text, message.chat.id, openai_request.QuestionType.public_session)
            bot.reply_to(message, response)

bot.infinity_polling()