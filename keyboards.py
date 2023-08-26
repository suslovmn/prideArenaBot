from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton




# mainKb = ReplyKeyboardMarkup()
pricesButton = KeyboardButton (text= 'Стоимость аренды')
phoneButton = KeyboardButton (text= 'Отложенный звонок')
callMeButton = KeyboardButton (text= 'Наш телефон')
managerPhoneButton = KeyboardButton (text= 'Наш адрес')

column1 = [pricesButton, phoneButton]
column2 = [callMeButton, managerPhoneButton]


mainKb = ReplyKeyboardMarkup(
    keyboard=list(zip(column1, column2)),
    resize_keyboard=True
)




trafficKb = ReplyKeyboardMarkup()
googleButton = KeyboardButton (text= 'Google')
facebookButton = KeyboardButton (text= 'Facebook')
nativeButton = KeyboardButton (text= 'Native')
popsPushButton = KeyboardButton (text= 'Pops/Push')
aso = KeyboardButton (text= 'Aso')
tikTok = KeyboardButton (text= 'Tik-Tok')
other = KeyboardButton (text= 'Другое:')

trafficKb\
    .add(googleButton)\
    .add(facebookButton)\
    .add(nativeButton)\
    .add(popsPushButton)\
    .add(aso)\
    .add(tikTok)\
    .add(other)


verticalKb = ReplyKeyboardMarkup()
nutraButton = KeyboardButton(text= 'Nutra')
iGamingButton = KeyboardButton(text= 'iGaming')
daitingButton = KeyboardButton(text= 'Daiting')
spbsButton = KeyboardButton(text= 'SP/BS')
cryptoButton = KeyboardButton(text= 'Crypto')
otherButton = KeyboardButton(text= 'Другое:')

verticalKb\
    .add(nutraButton)\
    .add(iGamingButton)\
    .add(daitingButton)\
    .add(spbsButton)\
    .add(cryptoButton)\
    .add(otherButton)


moneyYesNoKb = ReplyKeyboardMarkup()
yesButton = KeyboardButton(text= 'Окей, не проблема 💪')
noButton = KeyboardButton(text= 'Нет, не готов (')
moneyYesNoKb.add(yesButton).add(noButton)


yourAgeKb = ReplyKeyboardMarkup()
moreThan18Button = KeyboardButton(text= 'Да')
lessThan18Button = KeyboardButton(text= 'Нет')
yourAgeKb.add(moreThan18Button).add(lessThan18Button)