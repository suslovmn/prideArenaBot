import os
import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from dotenv import load_dotenv, find_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from botMessages import greetingMessage, phoneButtonText, \
    callMeButtonText, ourAdressButtonText
from keyboards import mainKb

load_dotenv(find_dotenv())

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'creds.json'
SPREADSHEET_ID = os.getenv('GOOGLE_SHET_ID')

bot = Bot(token=os.getenv('BOT_TOKEN'))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class UserForm(StatesGroup):
    mainMenu = State()
    yourPhoneState = State()


@dp.message_handler(commands=['start'], state='*')
async def welcome(message: types.Message):
    await message.reply(greetingMessage, reply_markup=mainKb)
    await UserForm.mainMenu.set()


@dp.message_handler(state=UserForm.mainMenu)
async def process_name(message: types.Message):

    if message.text == "Стоимость аренды":
        print(message.text)
        with open('resourсes/prices.jpeg', 'rb') as photo:
            await message.reply_photo(photo)
    if message.text == callMeButtonText:
        await message.reply("Оставьте номер телефона мы вам перезвоним:",
                                reply_markup=ReplyKeyboardRemove())
        await UserForm.yourPhoneState.set()
    if message.text == phoneButtonText:
        await message.reply("Наш телефон: +79217832332, звоните с 10-00 до 22-00")
    if message.text == ourAdressButtonText:
        address_link = '<a href="https://yandex.ru/navi/?whatshere%5Bzoom%5D=18&whatshere%5Bpoint%5D=30.344741%2C59.876228">адрес</a>'
        reply_text = f"Наш {address_link} - ул. Благодатная улица, 67В, ближайшие метро Электросила и Бухарестская"
        await message.reply(reply_text, parse_mode='HTML')


@dp.message_handler(state=UserForm.yourPhoneState)
async def process_yourPhoneState(message: types.Message, state: FSMContext):

    if not is_valid_phone_number(message.text):
        await message.reply(text='Вы ввели неверный номер телефона, попробуйте еще раз или позвоните администратору')
        await UserForm.yourPhoneState.set()
        return

    async with state.proxy() as data:
        data['phone'] = message.text

        # отправляем сообщение в админскую группу
        chat_id_logs = str(-915214450)

        message_text = f'Только что клиент оставил свой телефон для звонка!\n\n'
        message_text += f'Его телефон:\n- {data.values()}\n\n'
        message_text += f'Данные участника:\n'
        message_text += f'Имя в Telegram: {message.from_user.first_name}\n'
        message_text += f'Фамилия в Telegram: {message.from_user.last_name}\n'
        message_text += f'Username в Telegram: {message.from_user.username}\n'
        message_text += f'ID участника в Telegram: {message.from_user.id}\n'
        await bot.send_message(chat_id=chat_id_logs, text=message_text)

        await message.reply("Наш менеджер свяжется с вами в ближайшее время", reply_markup=mainKb)
        await UserForm.mainMenu.set()

        # Добавляем данные в гугл таблицу
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        sheets_service = build('sheets', 'v4', credentials=credentials)
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        values = []
        values.append([
            data['phone'],
            message.from_user.username,
            current_time
        ])

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
            await bot.send_message(chat_id=chat_id_logs, text=message.from_user.id)
            print('An error occurred: {0}'.format(error))

def is_valid_phone_number(phone_number):
    valid_chars = set("0123456789() -+")
    if set(phone_number) <= valid_chars and 7 <= len(phone_number) <= 12:
        return True
    return False


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
