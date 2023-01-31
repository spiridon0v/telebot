import asyncio
import os
import re
import requests
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from bs4 import BeautifulSoup as b
from urllib.request import urlretrieve

url = 'https://school42.nubex.ru/11282/'


bot = Bot('5917714388:AAG_rWR8bbP-xLTFouT9qHWpjmc-mfk4RtM')
dp = Dispatcher(bot)

button = KeyboardButton("Замена")
ReplyButton = ReplyKeyboardMarkup(resize_keyboard=True).add(button)

users = {}


def parse_url():
    r = requests.get(url).text
    soup = b(r, 'html.parser')
    block = soup.find_all('a', href=True, target=True)
    link = block[-4].get('href')  # ссылка
    return link


def parse_date():
    r = requests.get(url).text
    soup = b(r, 'html.parser')
    block = soup.find_all('a', href=True, target=True)
    date = block[-4].text.replace('.docx', '')
    date = re.sub("[^0-9,.]", "", date)
    return date


def download(url):
    filename = os.path.basename(url)
    if not os.path.isdir(os.path.join('./Documents')):
        os.mkdir("Documents")
    if not os.path.isfile(os.path.join('./Documents', filename)):
        urlretrieve(url, os.path.join('./Documents', filename))
    document = open(f'./Documents/{filename}', 'rb')
    return document


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.chat.id in users:
        await message.answer('Ты уже отправлял /start.')

    else:
        await message.answer(
            f'Привет, {message.from_user.full_name}! 😊 \nНажми на кнопку, и я буду автоматически присылать тебе замены!',
            reply_markup=ReplyButton)
        users[message.chat.id] = {'clicked_button': False}


@dp.message_handler(content_types=['text'])
async def reaction(message: types.Message):
    if message.text == 'Замена':
        if users[message.chat.id]['clicked_button'] == False:
            users[message.chat.id]['clicked_button'] = True
            url = parse_url()
            document = download(url)
            await message.answer_document(document,
                                          caption=f'Изменения в расписании на {parse_date()}. \nЖди, когда я пришлю новые! 😉')
            post = hash(parse_url())
            while True:
                post2 = hash(parse_url())
                if post2 != post:
                    url = parse_url()
                    document = download(url)
                    await message.answer_document(document, caption=f'Изменения в расписании на {parse_date()}!')
                    post = post2
                await asyncio.sleep(300)

        else:
            await message.answer('Я уже работаю!', reply_markup=ReplyButton)


if __name__ == '__main__':
    print(parse_date())
    executor.start_polling(dp, skip_updates=True)
