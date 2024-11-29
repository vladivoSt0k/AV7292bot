import os
from background import keep_alive
import pip
pip.main(['install', 'pytelegrambotapi'])
import telebot
import time

# очищаем все файлы или создаем пустые
with open('messages.txt', 'w') as f:
    f.write("")
with open('user_id.txt', 'w') as f:
    f.write("")
with open('from_esp.txt', 'w') as f:
    f.write("")
with open('from_tg.txt', 'w') as f:
    f.write("")


def get_last_update(now, last):
    # функция для определения времени получения данных от микроконтроллера
    diff = now - last
    if diff < 60:
        return f"{int(diff)} сек назад"
    elif diff < 60 * 60:
        return f"{int(diff / 60)} мин назад"
    elif diff < 60 * 60 * 24:
        return f"{int(diff / 60 / 24)} ч назад"
    else:
        return "Более дня назад"


bot = telebot.TeleBot(os.environ['TOKEN'])  # Создаем бот

# Создание клавиатур, для удобной коммуникации с пользователем
start_keyboard = telebot.types.InlineKeyboardMarkup()
start_keyboard.add(
    telebot.types.InlineKeyboardButton('Получить информацию', callback_data='info'),
    telebot.types.InlineKeyboardButton('Управлять устройством', callback_data='control')
)

control_keyboard = telebot.types.InlineKeyboardMarkup()
control_keyboard.add(
    telebot.types.InlineKeyboardButton('Включить', callback_data='on'),
    telebot.types.InlineKeyboardButton('Выключить', callback_data='off')
)


# Клавиатуры будут прикреплены к сообщениям бота

# На любое сообщение пользователя присылаем варианты действий
# Как вариант, обрабатывать команду /start от пользователя
@bot.message_handler(content_types=['text'])
def get_text_message(message):
    bot.send_message(message.from_user.id, "Что вы хотите сделать?", reply_markup=start_keyboard)


# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def func(call):
    bot.answer_callback_query(call.id)  # подтверждаем боту, что действие по кнопке выполнено
    with open('user_id.txt', 'w') as f:
        f.write(str(call.from_user.id))  # записываем в файл user_id. Он понадобится для отправки сообщений
    if call.data == 'info':  # нажата кнопка с callback_data='info', получаем информацию из файла
        with open("from_esp.txt", "r") as f:  # читаем файл
            temp, light, time_last = f.readlines()[0].split(';')  # получаем значения переменных
            last_update = get_last_update(time.time(), float(time_last))  # и время получения данных
        # отправляем сообщение пользователю
        bot.send_message(call.from_user.id,
                         f"Все хорошо, \nТемпература: {temp} \nОсвещение: {'включено' if light == '1' else 'выключено'}\nОбновлено: {last_update}",
                         reply_markup=start_keyboard)
    if call.data == 'control':  # нажата кнопка с callback_data='control'
        bot.send_message(call.from_user.id, "Вот что можно сделать:", reply_markup=control_keyboard)
    if call.data == 'on':  # нажата кнопка с callback_data='on'
        bot.send_message(call.from_user.id, "Свет скоро включится")  # отправляем сообщение пользователю
        with open('from_tg.txt', 'w') as f:  # записываем в файл действие, которое хотим сделать
            f.write('1')  # включить свет
    if call.data == 'off':
        bot.send_message(call.from_user.id, "Свет скоро выключится")
        with open('from_tg.txt', 'w') as f:
            f.write('0')  # выключить свет


keep_alive()  # запуск веб-сервера из файла background.py
bot.infinity_polling()