from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from config import TOKEN

from database import BotDataBase

import keyboard

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

database = BotDataBase()


# СДЕЛАТЬ УПРАВЛЕНИЕ ЧЕРЕЗ МЕНЮ И ПРИ ВХОДЕ В НЕГО ДОБАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    database.db_add_users(message.from_user.id, message.from_user.username)
    # DEBUG ANSWER
    await message.reply("Привет, команды бота:\n/add\n/remove\n/list\n/price")
    # DEBUG ANSWER

@dp.message_handler(commands=['add'])
async def add_article(message: types.Message):
    # добавить ответ, что артикул уже есть
    answer = database.db_add_favorite_articles(message.from_user.id, message.get_args())
    await bot.send_message(message.from_user.id, answer)

@dp.message_handler(commands=['remove'])
async def remove_article(message: types.Message):
    # добавить ответ, что артикула и так нет
    answer = database.db_remove_favorite_articles(message.from_user.id, message.get_args())
    await bot.send_message(message.from_user.id, answer)

@dp.message_handler(commands=['list'])
async def remove_article(message: types.Message):
    articles = database.db_show_favorite_articles(message.from_user.id)
    await bot.send_message(message.from_user.id, articles)


if __name__ == '__main__':
    executor.start_polling(dp)
