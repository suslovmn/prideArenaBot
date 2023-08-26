import os

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor
from dotenv import load_dotenv, find_dotenv

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


# Контакты менеджера для брони
# информация по ценам
# где находимся
# оставьте телефон мы вам перезвоним

# потом будет
# оплатите
# eзнать актуальное расписание


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
        await message.reply("Информационное сообщение с ценами")
    if message.text == callMeButtonText:
        await message.reply("Оставьте номер телефона мы вам перезвоним:",
                                reply_markup=ReplyKeyboardRemove())
        await UserForm.yourPhoneState.set()
    if message.text == phoneButtonText:
        await message.reply("Наш телефон: +79217832332, звоните с 10-00 до 22-00")
    if message.text == ourAdressButtonText:
        await message.reply("ул. Благодатная улица, 67В ближайшие метро Электросила и Бухарестская")

@dp.message_handler(state=UserForm.yourPhoneState)
async def process_other_traffic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        await message.reply("Наш менеджер свяжется с вами в ближайшее время", reply_markup=mainKb)
        await UserForm.mainMenu.set()

# @dp.message_handler(state=UserForm.email)
# async def process_email(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['email'] = message.text
#
#         await state.finish()
#         await message.reply("Спасибо, что заполнил заявку! Для приобретения билета напиши @affstyle_m",
#                             reply_markup=ReplyKeyboardRemove())
#
#         # отправляем сообщение в админскую группу
#         chat_id_logs = str(-814556788)
#
#         message_text = f'Только что зарегистрировался новый участник!\n\n'
#         message_text += f'Данные, которые он заполнил:\n- {data.values()}\n\n'
#         message_text += f'Реальные данные участника:\n'
#         message_text += f'Имя в Telegram: {message.from_user.first_name}\n'
#         message_text += f'Фамилия в Telegram: {message.from_user.last_name}\n'
#         message_text += f'Username в Telegram: {message.from_user.username}\n'
#         message_text += f'ID участника в Telegram: {message.from_user.id}\n'
#
#         await bot.send_message(chat_id=chat_id_logs, text=message_text)
#
#         # Добавляем данные в гугл таблицу
#         credentials = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#
#         sheets_service = build('sheets', 'v4', credentials=credentials)
#
#         values = []
#         values.append([
#             data['name'],
#             data['traffic'],
#             data['vertical'],
#             data['moneyYesNo'],
#             data['moreThan18Age'],
#             data['tgNickName'],
#             data['email'],
#             message.from_user.username
#         ])
#
#         body = {
#             'values': values
#         }
#
#         try:
#             result = sheets_service.spreadsheets().values().append(
#                 spreadsheetId=SPREADSHEET_ID, range='A2:H',
#                 valueInputOption='RAW', body=body).execute()
#
#             print('{0} cells updated.'.format(result.get('updatedCells')))
#         except HttpError as error:
#             await bot.send_message(chat_id=chat_id_logs,
#                                    text='этот участник не добавилсяв гугл таблицу из-за ошибки {0}'.format(error))
#             print('An error occurred: {0}'.format(error))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
