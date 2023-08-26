from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from keyboards import trafficKb, verticalKb, moneyYesNoKb, yourAgeKb, mainKb
from botMessages import greetingMesage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
from dotenv import load_dotenv, find_dotenv

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
    trafficSource = State()
    verticalSource = State()
    moneyYesNo = State()
    ageQuestion = State()
    tgNickename = State()
    email = State()

    otherTrafficSource = State()
    otherVerticalSource = State()





@dp.message_handler(commands=['start'], state='*')
async def welcome(message: types.Message):
    await message.reply(greetingMesage, reply_markup=mainKb)
    await UserForm.mainMenu.set()

@dp.message_handler(state=UserForm.mainMenu)
async def process_name(message: types.Message):

    await message.reply("Чем я могу Вам помочь?", reply_markup=mainKb)
    await UserForm.mainMenu.set()


@dp.message_handler(commands=['start'], state='*')
async def welcome(message: types.Message):
    await message.reply(greetingMesage, reply_markup=mainKb)
    await UserForm.mainMenu.set()


prices_text = "Стоимость аренды:\nОфис - 500 руб./кв.м в месяц\nКоворкинг - 300 руб./место в день"


# Обработчик нажатия на кнопку "Стоимость аренды"
async def on_prices_callback(callback_query: CallbackQuery):
    # Отправляем сообщение с текстом стоимости аренды
    await bot.send_message(callback_query.from_user.id, prices_text)

# Привязываем обработчик к кнопке "Стоимость аренды"
dp.register_callback_query_handler(on_prices_callback, text='Стоимость аренды')




@dp.message_handler(state=UserForm.trafficSource)
async def process_traffic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Другое:":
            await message.reply("Напиши какой именно источник трафика ты используешь.",
                                reply_markup=ReplyKeyboardRemove())
            await UserForm.otherTrafficSource.set()
        else:
            data['traffic'] = message.text
            await message.reply("С какой вертикалью ты работаешь?",
                                reply_markup=verticalKb)
            await UserForm.verticalSource.set()


@dp.message_handler(state=UserForm.otherTrafficSource)
async def process_other_traffic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['traffic'] = message.text
        await message.reply("С какой вертикалью ты работаешь?",
                            reply_markup=verticalKb)
        await UserForm.verticalSource.set()



@dp.message_handler(state=UserForm.verticalSource)
async def process_vertical(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "Другое:":
            await message.reply("Напиши, пожалуйста, какую именно вертикаль ты используешь.",
                                reply_markup=ReplyKeyboardRemove())
            await UserForm.otherVerticalSource.set()
        else:
            data['vertical'] = message.text
            await message.reply("Тикет стоит 50$",
                                reply_markup=moneyYesNoKb)
            await UserForm.moneyYesNo.set()

        # await message.reply("Тикет будет стоить 50$, работает как фильтр на ребят. В ином случае придется покупать тикет на месте,а они могут быть дороже, имей ввиду.",
        #                     reply_markup=moneyYesNoKb)
        # await UserForm.moneyYesNo.set()

@dp.message_handler(state=UserForm.otherVerticalSource)
async def process_other_vertical(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vertical'] = message.text
        await message.reply("Тикет будет стоить 50$, работает как фильтр на ребят. В ином случае придется покупать тикет на месте,а они могут быть дороже, имей ввиду.",
                            reply_markup=moneyYesNoKb)
        await UserForm.moneyYesNo.set()


@dp.message_handler(state=UserForm.moneyYesNo)
async def process_money(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['moneyYesNo'] = message.text

        await message.reply("Тебе есть 18+ лет? (слишком молодых мы не можем пустить на мероприятие)",
                            reply_markup=yourAgeKb)
        await UserForm.ageQuestion.set()


@dp.message_handler(state=UserForm.ageQuestion)
async def process_age(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['moreThan18Age'] = message.text

        await message.reply("Укажи телеграм на который писать менеджеру для связи с тобой (вдруг у тебя он скрыт или ты пишешь с рабочего), чтобы вручить тебе билет на тусовку",
                            reply_markup=ReplyKeyboardRemove())
        await UserForm.tgNickename.set()


@dp.message_handler(state=UserForm.tgNickename)
async def process_tgNickName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tgNickName'] = message.text

        await message.reply("Ну и почту добавь, для рассылочки!")
        await UserForm.email.set()


@dp.message_handler(state=UserForm.email)
async def process_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text

        await state.finish()
        await message.reply("Спасибо, что заполнил заявку! Для приобретения билета напиши @affstyle_m",
                            reply_markup=ReplyKeyboardRemove())

        # отправляем сообщение в админскую группу
        chat_id_logs = str(-814556788)

        message_text = f'Только что зарегистрировался новый участник!\n\n'
        message_text += f'Данные, которые он заполнил:\n- {data.values()}\n\n'
        message_text += f'Реальные данные участника:\n'
        message_text += f'Имя в Telegram: {message.from_user.first_name}\n'
        message_text += f'Фамилия в Telegram: {message.from_user.last_name}\n'
        message_text += f'Username в Telegram: {message.from_user.username}\n'
        message_text += f'ID участника в Telegram: {message.from_user.id}\n'

        await bot.send_message(chat_id=chat_id_logs, text=message_text)


        # Добавляем данные в гугл таблицу
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        sheets_service = build('sheets', 'v4', credentials=credentials)

        values = []
        values.append([
            data['name'],
            data['traffic'],
            data['vertical'],
            data['moneyYesNo'],
            data['moreThan18Age'],
            data['tgNickName'],
            data['email'],
            message.from_user.username
        ])

        body = {
            'values': values
        }

        try:
            result = sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID, range='A2:H',
                valueInputOption='RAW', body=body).execute()

            print('{0} cells updated.'.format(result.get('updatedCells')))
        except HttpError as error:
            await bot.send_message(chat_id=chat_id_logs,
                                   text='этот участник не добавилсяв гугл таблицу из-за ошибки {0}'.format(error))
            print('An error occurred: {0}'.format(error))



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)





