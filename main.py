import asyncio
import contextlib
import datetime
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from dotenv import load_dotenv, find_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from botMessages import greetingMessage, phoneButtonText, callMeButtonText, ourAdressButtonText
from keyboards import mainKb

load_dotenv(find_dotenv())

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'creds.json'
SPREADSHEET_ID = os.getenv('GOOGLE_SHET_ID')


class UserForm(StatesGroup):
    mainMenu = State()
    yourPhoneState = State()

async def welcome(message: types.Message, bot: Bot, state: FSMContext):
    await message.reply(greetingMessage, reply_markup=mainKb)
    await state.set_state(UserForm.mainMenu)

async def process_name(message: types.Message, bot: Bot, state: FSMContext):
    if message.text == "Стоимость аренды":
        await message.reply_photo(FSInputFile('resourсes/prices.jpeg'))

    elif message.text == callMeButtonText:
        await message.reply("Оставьте номер телефона мы вам перезвоним:",
                            reply_markup=ReplyKeyboardRemove())
        await state.set_state(UserForm.yourPhoneState)
    elif message.text == phoneButtonText:
        await message.reply("Наш телефон: +79119050078, звоните с 10-00 до 22-00")
    elif message.text == ourAdressButtonText:
        address_link = '<a href="https://yandex.ru/navi/?whatshere%5Bzoom%5D=18&whatshere%5Bpoint%5D=30.344741%2C59.876228">адрес</a>'
        reply_text = f"Наш {address_link} - ул. Благодатная 67В\n" \
                     f"15 минут пешком от м. Электросила,\n" \
                     f"15 минут пешком от м. Бухарестская\n" \
                     f"3 минуты пешком до остановки общественного транспорта:\n\n" \
                     f"Трамваи: 43, 45\n" \
                     f"Автобусы: 12, 36, 95, 159\n" \
                     f"Троллейбусы: 36, 39"
        await message.reply(reply_text, parse_mode='HTML')
    else:
        await message.reply("Непонятная команда, давайте попробуем с начала", reply_markup=mainKb)


async def process_yourPhoneState(message: types.Message, bot: Bot, state: FSMContext):
    if not is_valid_phone_number(message.text):
        await message.reply(text='Вы ввели неверный номер телефона, попробуйте еще раз или позвоните администратору')
        await state.set_state(UserForm.yourPhoneState)
        return

        # отправляем сообщение в админскую группу
    chat_id_logs = str(-915214450)

    message_text = f'Только что клиент оставил свой телефон для звонка!\n\n'
    message_text += f'Его телефон:\n- {message.text}\n\n'
    message_text += f'Данные участника:\n'
    message_text += f'Имя в Telegram: {message.from_user.first_name}\n'
    message_text += f'Фамилия в Telegram: {message.from_user.last_name}\n'
    message_text += f'Username в Telegram: {message.from_user.username}\n'
    message_text += f'ID участника в Telegram: {message.from_user.id}\n'
    await bot.send_message(chat_id=chat_id_logs, text=message_text)

    await message.reply("Наш менеджер свяжется с вами в ближайшее время", reply_markup=mainKb)
    await state.set_state(UserForm.mainMenu)

    # Добавляем данные в гугл таблицу
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    sheets_service = build('sheets', 'v4', credentials=credentials)
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    values = [[
        message.text,
        message.from_user.username,
        current_time
    ]]

    body = {
        'values': values
    }

    try:
        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range='A2:C',
            valueInputOption='RAW', body=body).execute()

        print('{0} cells updated.'.format(result.get('updatedCells')))
    except HttpError as error:
        await bot.send_message(chat_id=chat_id_logs,
                               text='этот участник не добавилсяв гугл таблицу из-за ошибки {0}'.format(error))
        await bot.send_message(chat_id=chat_id_logs, text=str(message.from_user.id))
        print('An error occurred: {0}'.format(error))


def is_valid_phone_number(phone_number):
    valid_chars = set("0123456789() -+")
    if set(phone_number) <= valid_chars and 7 <= len(phone_number) <= 12:
        return True
    return False


async def start():
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.register(welcome, Command(commands=['start']))
    dp.message.register(process_yourPhoneState, UserForm.yourPhoneState)
    dp.message.register(process_name)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as ex:
        logging.error(f"[!!! - Exception] - {ex}", exc_info=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        asyncio.run(start())

