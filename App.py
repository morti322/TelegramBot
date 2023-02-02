import telebot
from telebot import types

from Config import TOKEN, keys
from Extensions import APIException, CryptoConverter

bot = telebot.TeleBot(TOKEN)


def create_markup(base=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = []
    for key in keys.keys():
        if key != base:
            buttons.append(types.KeyboardButton(key.capitalize()))
    markup.add(*buttons)
    return markup


@bot.message_handler(commands=["start", "help"])
def handle_start_help(message: telebot.types.Message):
    text = "Чтобы начать введите команду:\n" \
           "<имя валюты> <в какую валюту переводить> <количество переводимой валюты>,\n" \
           "например: евро рубль 1\n" \
           "\n" \
           "Так же вы можете переводить валюту с помощь /convert\n" \
           "\n" \
           "Список доступных команд:\n" \
           "/convert - начать конвертацию валют\n" \
           "/help, /start - помощь по боту\n" \
           "/values - показать доступные валюты\n" \
           "/info - о программе"
    bot.reply_to(message, text)


@bot.message_handler(commands=["values"])
def handle_values(message: telebot.types.Message):
    text = 'Доступные валюты:\n'
    for key in keys.keys():
        text += '\n' + key
    bot.reply_to(message, text)


@bot.message_handler(commands=["info"])
def handle_info(message: telebot.types.Message):
    text = 'Простой бот, для конвертации валют.\n' \
           '/help или /start - для знакомства с ботом.'
    bot.reply_to(message, text)


@bot.message_handler(commands=["convert"])
def convert_handler(message: telebot.types.Message):
    text = "Введите валюту, из которой конвертировать"
    bot.send_message(message.chat.id, text, reply_markup=create_markup())
    bot.register_next_step_handler(message, base_handler)


def base_handler(message: telebot.types.Message):
    base = message.text.strip().lower()
    text = "Введите валюту, в которую конвертировать"
    bot.send_message(message.chat.id, text, reply_markup=create_markup(base))
    bot.register_next_step_handler(message, quote_handler, base)


def quote_handler(message: telebot.types.Message, base):
    quote = message.text.strip().lower()
    text = "Введите количество конвертируемой валюты"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, base, quote)


def amount_handler(message: telebot.types.Message, base, quote):
    amount = message.text.strip().replace(",", ".")

    try:
        total_base = CryptoConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка ввода параметров!\n{e}')
    else:
        amount = float(amount)
        text = f"Результат конвертации:\n" \
               f"{amount:,.2f} {base} = {total_base:,.2f} {quote}\n" \
               f"{amount:,.2f} {keys[base]} = {total_base:,.2f} {keys[quote]}"
        bot.send_message(message.chat.id, text)


@bot.message_handler(content_types=["text"])
def handle_convert(message: telebot.types.Message):
    values = message.text.lower().replace(",", ".").split()

    try:
        if len(values) != 3:
            raise APIException("Неверное количество параметров")
        base, quote, amount = values
        total_base = CryptoConverter.get_price(base, quote, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка ввода параметров!\n{e}')
    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду:\n{e}')
    else:
        amount = float(amount)
        text = f"Результат конвертации:\n" \
               f"{amount:,.2f} {base} = {total_base:,.2f} {quote}\n" \
               f"{amount:,.2f} {keys[base]} = {total_base:,.2f} {keys[quote]}"
        bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['photo', ])
def photo_factory(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Фото не принимается.')

@bot.message_handler(content_types=['voice', ])
def voice1(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Прости, много работы. \nПоговорим позже.')

@bot.message_handler(content_types=['sticker'])
def stic1(message: telebot.types.Message):
   bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOMY6WAdMw1TO1RLiHv6M807AcmZgsAAh4AA8A2TxOhYFstqwAB3gQsBA")

@bot.message_handler(content_types=['document', ])
def doc1(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'Прости, но я не понимаю тебя.')

@bot.message_handler(content_types=['audio', ])
def audio1(message: telebot.types.Message):
     bot.send_message(message.chat.id, 'Прости, но я не могу послушать это.')

@bot.message_handler(content_types=['video', ])
def video(message: telebot.types.Message):
    bot.send_message(message.chat.id, 'К сожалению сообщения такого формата я не пойму')


bot.polling()



