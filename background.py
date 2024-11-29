from flask import Flask
from flask import request
from threading import Thread
import time
import requests

app = Flask('')


@app.route('/')  # Создаем "главную страницу" которую будет пинговать UpTimeRobot
def home():
    return "I'm alive"


@app.route('/iot', methods=['GET'])  # создает ссылку /iot на которую будут приходить запросы
def iot():
    temp = request.args.get('temp')  # получаем параметры из GET-запроса
    light = request.args.get('light')
    with open('from_esp.txt', 'r') as f:  # читаем данные, полученные из ESP в прошлый раз
        old_temp, old_light, time_last = f.readlines()[0].split(';')
        if old_light == "0" and light == "1":  # и если старое состояние выкл, а новое вкл
            with open('messages.txt', 'w') as f_m:  # записываем в файл messages текст сообщения
                f_m.write("Свет включился")
        if old_light == "1" and light == "0":
            with open('messages.txt', 'w') as f_m:
                f_m.write("Свет выключился")
    with open('from_esp.txt', 'w') as f:  # записываем в файл новые значения
        f.write(f"{temp};{light};{time.time()}")

    with open('from_tg.txt', 'r') as f:  # читаем из файла действие, сделанное командой в телеграм боте
        new_state = f.read(1)  # т.к. у нас только 1 параметр Включить/выключить свет, читаем 1 символ
    return new_state  # возвращаем значение


# Для Flask-сервера это означает, что прочитанный символ будет показан на веб-странице https://сайт/iot


def run():  # функция запуска flask-сервера
    app.run(host='0.0.0.0', port=80)


def reminder():
    while True:
        with open('user_id.txt', 'r') as f:  # пытаемся прочитать user_id. Номер чата с пользователем
            lines = f.readlines()
            if len(lines) > 0:
                chat_id = lines[0]
            else:
                chat_id = None
        with open('messages.txt', 'r') as f:  # читаем файл с сообщением
            lines = f.readlines()
            if len(lines) > 0 and chat_id is not None:  # если есть user_id и сообщение
                text = lines[0]
                token = os.environ['TOKEN']
                requests.get(r"https://api.telegram.org/bot"
                             + token
                             + r"/sendMessage?chat_id=" + chat_id
                             + r"&text=" + text)
                # отправляем сообщение по специальной ссылке с использованием токена
        with open('messages.txt', 'w') as f:
            f.write("")  # очищаем файл с сообщениями
        time.sleep(0.3)


def keep_alive():  # запускаем flask и reminder в отдельных потоках
    t = Thread(target=run)
    t.start()
    tr = Thread(target=reminder)
    tr.start()