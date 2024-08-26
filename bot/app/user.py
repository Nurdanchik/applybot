import requests

import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram import Bot
from aiohttp import ClientSession, TCPConnector
import app.keyboards as kb
import app.config as config # Убедитесь, что импортировали config

TOKEN = config.TOKEN  # Получите токен из config

# UPLOAD_API = "http://127.0.0.1:8000/api/upload_user"
# GET_API = ""
upload_api = requests.get('http://127.0.0.1:8000/api/upload_user')
get_api = requests.get('http://127.0.0.1:8000/api/faces/code')
get_data = get_api.json()

user = Router()

# Initialize the bot with the token from config
bot = Bot(token=TOKEN)

@user.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        f"""
Hello, {message.from_user.full_name}!
Welcome to ApplyBot!
Use /help to get help!
Good luck!
""", reply_markup=kb.main
    )

@user.message(F.text == 'HELP')
async def help(message: Message):
    await message.answer(f'''
Hello, {message.from_user.full_name}!
How it is done: 
1. You start this bot.
2. You send a picture of you with the code.

You MUST follow the next rules:
1. The picture must contain ONLY YOUR FACE AND THE CODE, NOTHING ELSE (especially prints, text on your background, t-shirt, etc.)

If you have more questions or if you are having any issue, contact @admin
''')

@user.message(F.photo)
async def get_or_post_face(message: Message):
    photo_id = message.photo[-1].file_id
    file = await bot.get_file(photo_id)
    file_path = file.file_path

    # Download the photo from Telegram server using aiohttp with SSL verification disabled
    connector = TCPConnector(ssl=False)
    async with ClientSession(connector=connector) as session:
        async with session.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_path}') as response:
            if response.status == 200:
                photo_bytes = await response.read()
            else:
                await message.reply("Failed to download the image from Telegram.")
                return

    # Send the photo to your FastAPI server
    async with ClientSession() as session:
        async with session.post(upload_api, data={'image': ('photo.jpg', photo_bytes, 'image/jpeg')}) as resp:
            if resp.status == 200:
                result = await resp.json()
                # Send the result from FastAPI API back to the user
                await message.reply(f"Server responded: {result}")
            else:
                await message.reply("Failed to upload the image to the server.")


@user.message(Command('get_users'))
async def get_user(message: Message):
    await message.answer(text= f'{get_data}')