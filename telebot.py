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

uni = ['%u0410', '%u0411', '%u0412', '%u0413', '%u0414', '%u0415', '%u0401', '%u0416', '%u0417', '%u0418', '%u0419',
       '%u041A', '%u041B', '%u041C', '%u041D', '%u041E', '%u041F', '%u0420', '%u0421', '%u0422', '%u0423', '%u0424',
       '%u0425', '%u0426', '%u0427', '%u0428', '%u0429', '%u042A', '%u042B', '%u042C', '%u042D', '%u042E', '%u042F',
       '%u0430', '%u0431', '%u0432', '%u0433', '%u0434', '%u0435', '%u0451', '%u0436', '%u0437', '%u0438', '%u0439',
       '%u043A', '%u043B', '%u043C', '%u043D', '%u043E', '%u043F', '%u0440', '%u0441', '%u0442', '%u0443', '%u0444',
       '%u0445', '%u0446', '%u0447', '%u0448', '%u0449', '%u044A', '%u044B', '%u044C', '%u044D', '%u044E', '%u044F',
       '%20']
rus = ['Рђ', 'Р‘', 'Р’', 'Р“', 'Р”', 'Р•', 'РЃ', 'Р–', 'Р—', 'Р', 'Р™', 'Рљ', 'Р›', 'Рњ', 'Рќ', 'Рћ', 'Рџ', 'Р ', 'РЎ',
       'Рў', 'РЈ', 'Р¤', 'РҐ', 'Р¦', 'Р§', 'РЁ', 'Р©', 'РЄ', 'Р«', 'Р¬', 'Р', 'Р®', 'РЇ', 'Р°', 'Р±', 'РІ', 'Рі', 'Рґ',
       'Рµ', 'С‘', 'Р¶', 'Р·', 'Рё', 'Р№', 'Рє', 'Р»', 'Рј', 'РЅ', 'Рѕ', 'Рї', 'СЂ', 'СЃ', 'С‚', 'Сѓ', 'С„', 'С…', 'С†',
       'С‡', 'С€', 'С‰', 'СЉ', 'С‹', 'СЊ', 'СЌ', 'СЋ', 'СЏ', ' ']

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
    for i in range(len(uni)):
        link = link.replace(rus[i], uni[i])
    print(link)
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
