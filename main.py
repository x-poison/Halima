from datetime import datetime
from pyrogram import Client, filters
import datetime
import pycountry
import pytz
import requests
import telebot
import openai
import re
openai.api_key = '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'


bot = telebot.TeleBot('5627044029:AAE7fAZGpds2Jf2InRSzeaCHWQk-6i0BwHA')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Hello, Am Halima Bot how can i assist you today')

@bot.message_handler(commands=['joke'])
def joke(message):
        joke_response = requests.get('https://official-joke-api.appspot.com/random_joke')
        if joke_response.status_code == 200:
            joke_data = joke_response.json()
            setup = joke_data['setup']
            punchline = joke_data['punchline']
            bot.send_message(message.chat.id, f"{setup}\n{punchline}")
        else:
            bot.send_message(message.chat.id, 'Sorry, I couldn\'t fetch a joke at the moment. Please try again later.')
@bot.message_handler(commands=['time'])
def get_time(message):
    country_code = message.text.split()[1] if len(message.text.split()) > 1 else None

    if country_code is None:
        bot.reply_to(message, 'Please provide a country prefix')
        return

    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if country is None:
            raise ValueError
        timezones = pytz.country_timezones.get(country.alpha_2)
        if not timezones:
            raise pytz.UnknownTimeZoneError
        country_timezone = pytz.timezone(timezones[0])
    except (ValueError, pytz.UnknownTimeZoneError):
        bot.reply_to(message, 'Invalid Prefix')
        return

    current_time = datetime.datetime.now(country_timezone)
    formatted_time = current_time.strftime('%H:%M:%S')
    formatted_date = current_time.strftime('%Y-%m-%d')
    formatted_day = current_time.strftime('%A')

    response = f'𝐓𝐢𝐦𝐞 & 𝐃𝐚𝐭𝐞\n\n𝐂𝐨𝐮𝐧𝐭𝐫𝐲: {country.name}\n𝐓𝐢𝐦𝐞: {formatted_time}\n𝐃𝐚𝐭𝐞: {formatted_date}\n𝐃𝐚𝐲: {formatted_day}'

    bot.reply_to(message, response)

@bot.message_handler(commands=['chatinfo'])
def get_chat_info(message):
    chat_id = message.chat.id
    chat_type = message.chat.type

    if chat_type == 'private':
        user_id = message.from_user.id
        username = message.from_user.username
        response = f'𝐂𝐡𝐚𝐭 𝐈𝐃: {chat_id}\n𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {username}\n𝐔𝐬𝐞𝐫 𝐈𝐃: {user_id}'
        bot.reply_to(message, response)
        return

    chat_title = message.chat.title

    response = f'𝐂𝐡𝐚𝐭 𝐈𝐃: {chat_id}\n𝐂𝐡𝐚𝐭 𝐓𝐢𝐭𝐥𝐞: {chat_title}\n𝐂𝐡𝐚𝐭 𝐓𝐲𝐩𝐞: {chat_type.capitalize()}\n'

    if chat_type in ['group', 'supergroup']:
        chat_info = bot.get_chat(chat_id)
        members_count = bot.get_chat_members_count(chat_id)
        response += f'𝐌𝐞𝐦𝐛𝐞𝐫𝐬: {members_count}\n'

        administrators = bot.get_chat_administrators(chat_id)

        owner_mention = None
        admin_mentions = []
        for admin in administrators:
            if admin.status == 'creator':
                if admin.user.username:
                    owner_mention = f'@{admin.user.username}'
                else:
                    owner_mention = admin.user.first_name
            if admin.user.username:
                admin_mention = f'@{admin.user.username}'
            else:
                admin_mention = admin.user.first_name
            admin_mentions.append(admin_mention)

        response += f'𝐎𝐰𝐧𝐞𝐫: {owner_mention if owner_mention else "None"}\n'
        response += f'𝐀𝐝𝐦𝐢𝐧𝐬: {", ".join(admin_mentions)}'

    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    response = generate_response(message.text)
    bot.reply_to(message, response)

class MaxWordLimitExceededError(Exception):
    pass

def generate_response(text):
    max_word_limit = 150000

    word_count = len(text.split())

    if word_count > max_word_limit:
        raise MaxWordLimitExceededError(f"The input exceeds the maximum word limit of {max_word_limit}. Please reduce the text length.")

    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=text,
        max_tokens=4000
    )

    generated_text = response.choices[0].text.strip()
    return generated_text

@bot.message_handler(commands=['pin'])
def pin_message(message):
    if message.from_user.id == YOUR_ADMIN_ID:
        chat_id = message.chat.id
        message_id = message.reply_to_message.message_id
        bot.pin_chat_message(chat_id, message_id)
        bot.reply_to(message, "Message pinned successfully.")
    else:
        bot.reply_to(message, "You need to be an admin to use this command.")




bot.polling()
