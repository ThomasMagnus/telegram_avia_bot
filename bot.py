import telebot
from main import Data, Tickets
from telebot import types
import re
from dateutil.parser import parse

bot = telebot.TeleBot(YOUR_TELEBOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я твой помошник для поиска дешевых авиабилетов!'
                                      'Введите маршрут через пробел(Москва/Владивосток)',
                     parse_mode=None)


@bot.message_handler(content_types=['text'])
def get_city(message):
    if not Data.city:
        Data.city = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Да")
        btn2 = types.KeyboardButton("Нет")
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Маршрут туда и обратно?", reply_markup=markup)
        return

    if message.text == "Да":
        Data.route = message.text
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Введите дату вылета и прилета через дефис (01.01.2022-10.02.2022)",
                         reply_markup=markup)
        return
    elif message.text == "Нет":
        markup = types.ReplyKeyboardRemove()
        Data.route = message.text
        bot.send_message(message.chat.id, "Введите дату вылета", reply_markup=markup)
        return

    if not Data.date:
        if not re.match(r'\d{2}.\d{2}.\d{4}-\d{2}.\d{2}.\d{4}', message.text):
            bot.send_message(message.chat.id, "Вы неправильно ввели дату! Будьте внимательны(01.01.2022-10.02.2022)!")
            return
        else:
            Data.date = message.text
            bot.send_message(message.chat.id, "Отлично! Запрос обрабатывается!")
            tickets = Tickets(YOUR_AVIASALES_TOKEN, city=Data.city, route=Data.route,
                              route_date=Data.date)
            response = tickets.get_tickets()['data']
            print(tickets.get_tickets())
            for item in response:
                html_text = f'<a>{Data.city}</a>\n' \
                            f'<a>Туда: {parse(item["departure_at"]).strftime("%d.%m %H:%M")}</a>\n' \
                            f'<a>Обратно: {parse(item["return_at"]).strftime("%d.%m %H:%M")}</a>\n' \
                            f'<a>Цена: {item["price"]} руб.</a>\n' \
                            f'<a href="https://www.aviasales.ru/{item["link"]}">Источник</a>\n'
                bot.send_message(message.chat.id, html_text, parse_mode='html')
            Data.city = None
            Data.route = None
            Data.date = None
            return


if __name__ == '__main__':
    print("Бот активен!")
    bot.polling(none_stop=True)
