from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from botMessages import pricesButtonText, phoneButtonText, callMeButtonText, ourAdressButtonText

pricesButton = KeyboardButton(text=pricesButtonText)
phoneButton = KeyboardButton(text=phoneButtonText)
callMeButton = KeyboardButton(text=callMeButtonText)
managerPhoneButton = KeyboardButton(text=ourAdressButtonText)

column1 = [pricesButton, phoneButton]
column2 = [callMeButton, managerPhoneButton]

mainKb = ReplyKeyboardMarkup(
    keyboard=list(zip(column1, column2)),
    resize_keyboard=True
)

