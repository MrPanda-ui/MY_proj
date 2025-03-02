import telebot
import sqlite3
from telebot import types
users = {}
API_TOKEN = '7648826500:AAG8TvsNT9G9oMZh7y5z4Qk-_2Mo_SBiq9Y'#токен бота
bot = telebot.TeleBot(API_TOKEN)#подключение бота по токену
name , pas, surename, est, god = "", "", "", "", ""
d = int()
id = None

@bot.message_handler(commands=['start'])#команда старта
def handle_start(message):#создаем таблицу с ячейками
    conn = sqlite3.connect('tg.db', check_same_thread=False)#подключение к базе данных
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users(user_id int primary key, name varchar(50), surname varchar(50), study varchar(50), place varchar(255))')
    chat_id = message.chat.id
    global id
    id = message.from_user.id
    bot.send_message(message.chat.id, "Напишите /help чтобы показать все доступные команды")
    info = cursor.execute('SELECT 1 FROM users WHERE user_id=?', [id]).fetchone()#узнаем есть ли запись с таким же id пользователя
    if info is None:# Если пользователь не авторизовался
        bot.send_message(message.chat.id, "Авторизируйтесь чтобы продолжить работу с ботом")
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        button_save = types.KeyboardButton( text="Авторизоваться")
        keyboard.add(button_save)
        bot.send_message(chat_id, "Добро пожаловать в бота-тест по кибер-безопасности!!!", reply_markup=keyboard )
    else: #если пользователь уже авторизовался
        cursor.execute("SELECT * from users WHERE user_id=?", [id])
        records = cursor.fetchall()
        for row in records:# с помощью цикла находим 2ой и 3й столбец для приветствия с пользователем
            bot.send_message(chat_id, f"Приветствую {row[1]} {row[2]}!!!")
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
        button_gotov = telebot.types.KeyboardButton(text="Пройти опрос")
        keyboard.add(button_gotov)
        bot.send_message(chat_id, "Готов пройти тест?", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Авторизоваться')#команда авторизации, чтобы бот работал дальше и можно было составлять данные
def loginning(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите имя:")
    bot.register_next_step_handler(message, family)

def family(message):
    chat_id = message.chat.id
    global name
    name = message.text
    bot.send_message(chat_id, f"Отлично, {name}. Теперь укажите фамилию")
    bot.register_next_step_handler(message, surename)

def surename(message):
    chat_id = message.chat.id
    global surename
    surename = message.text
    bot.send_message(chat_id, f"Отлично, {surename} {name}. Теперь укажи кто ты по образованию")
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    button_school = telebot.types.KeyboardButton(text="Школьник")
    button_Student = telebot.types.KeyboardButton(text="Студент")
    keyboard.add(button_school, button_Student)
    bot.send_message(chat_id, "Выбери кем ты являешься:", reply_markup=keyboard)
    bot.register_next_step_handler(message, mesto)

def mesto(message):
    chat_id = message.chat.id
    global est
    est = message.text
    bot.send_message(chat_id, "Введите название образовательного учереждения:")
    bot.register_next_step_handler(message, education)

def education(message):
    chat_id = message.chat.id
    global pas
    pas = message.text
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_save = telebot.types.InlineKeyboardButton(text="Сохранить", callback_data='save_data')
    button_chage = telebot.types.InlineKeyboardButton(text="Изменить", callback_data='change_data')
    keyboard.add(button_save, button_chage)
    bot.send_message(chat_id, 'Сохранить данные?', reply_markup=keyboard)


    
@bot.callback_query_handler(func=lambda call: call.data == 'save_data')#вызов действия при нажатии кнопки "Сохранить"
def save_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    conn = sqlite3.connect('tg.db', check_same_thread=False)#подключение к базе данных
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO users VALUES (?, ?, ?, ?, ?)', (id, name, surename, pas, est))#внесение данных в таблицу
    conn.commit()#сохранение изменение
    cursor.close()#закрытие таблицы
    conn.close()#отключение от бд
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Данные сохранены!')
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1)
    button_gotov = telebot.types.KeyboardButton(text="Пройти опрос")
    keyboard.add(button_gotov)
    bot.send_message(chat_id, "Готов пройти тест?", reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: call.data == 'change_data')#вызов действия при нажатии кнопки "Изменить"
def change_btn(call):
    message = call.message
    chat_id = message.chat.id
    message_id = message.message_id
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text='Именение данных!')
    loginning(message)

@bot.message_handler(func=lambda message: message.text == 'Пройти опрос')#опрос состоящий из 5ти функций
def question(message):
    chat_id = message.chat.id
    global id
    conn = sqlite3.connect('tg.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS answer(user_id int primary key, marks int(10))')#создание таблицы с количиством ответов 
    info = cursor.execute('SELECT * FROM answer WHERE user_id=?', [id]).fetchone()
    if info is None:# условие проходил ли человек опрос
        keyboard = telebot.types.ReplyKeyboardMarkup()
        button_save = telebot.types.KeyboardButton(text="Да")
        button_chage = telebot.types.KeyboardButton(text="Нет")
        keyboard.add(button_save, button_chage)
        bot.send_message(chat_id, 'Представляет ли угрозу для вашего устройства незащищённое подключение по WI-FI в общественных местах?', reply_markup=keyboard)
        bot.register_next_step_handler(message, question_2)
    else:
        bot.send_message(chat_id, "Вы уже прошли тест")
        cursor.execute("SELECT * from answer Where user_id=?", [id])
        rec = cursor.fetchall()
        for row in rec:
            bot.send_message(chat_id, f"Ваш результат: {row[1]}/5")

@bot.message_handler(func=lambda message: message.text == 'Да' or message.text == 'Нет')
def question_2(message):
    chat_id = message.chat.id
    global d
    if message.text =="Да":
        d += 1
    else:
        d += 0
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_save = telebot.types.KeyboardButton(text="Является безопасным")
    button_chage = telebot.types.KeyboardButton(text="Является не безопасным",)
    keyboard.add(button_save, button_chage)
    bot.send_message(chat_id, 'Комбинация пароля который легко можно подобрать?', reply_markup=keyboard)
    bot.register_next_step_handler(message, question_3)

@bot.message_handler(func=lambda message: message.text == 'Является безопасным' or message.text == 'Является не безопасным')
def question_3(message):
    chat_id = message.chat.id
    global d
    if message.text =="Является не безопасным":
        d += 1
    else:
        d += 0
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_save = telebot.types.KeyboardButton(text="Не может")
    button_chage = telebot.types.KeyboardButton(text="Может")
    keyboard.add(button_save, button_chage)
    bot.send_message(chat_id, 'Может ли почтовое вложение от неизвастного пользователя нести вредоностное ПО?', reply_markup=keyboard)
    bot.register_next_step_handler(message, question_4)

@bot.message_handler(func=lambda message: message.text == 'Может' or message.text == 'Не может')
def question_4(message):
    chat_id = message.chat.id
    global d
    if message.text =="Может":
        d += 1
    else:
        d += 0
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_save = telebot.types.KeyboardButton(text="Клиенсткая, серверная, сетевая")
    button_chage = telebot.types.KeyboardButton(text="Персональная, корпоративная, государственная")
    button_cha = telebot.types.KeyboardButton(text="Локальная, глобальная, смешенная")
    keyboard.add(button_save, button_chage, button_cha)
    bot.send_message(chat_id, 'Виды информационной безопасности:', reply_markup=keyboard)
    bot.register_next_step_handler(message, question_5)

@bot.message_handler(func=lambda message: message.text == 'Персональная, корпоративная, государственная' or message.text == 'Клиенсткая, серверная, сетевая' or message.text == 'Локальная, глобальная, смешенная')
def question_5(message):
    chat_id = message.chat.id
    global d
    if message.text =="Персональная, корпоративная, государственная":
        d += 1
    else:
        d += 0
    keyboard = telebot.types.ReplyKeyboardMarkup()
    button_save = telebot.types.KeyboardButton(text="12344321")
    button_chage = telebot.types.KeyboardButton(text="qwerty1234")
    button_chag = telebot.types.KeyboardButton(text="fTfG_Ah`A2BlV{Z")
    button_cha = telebot.types.KeyboardButton(text="Yandex228")
    keyboard.add(button_save, button_chage, button_chag, button_cha)
    bot.send_message(chat_id, 'Какой из следующих паролей безопасный?', reply_markup=keyboard)
    bot.register_next_step_handler(message, result)

@bot.message_handler(func=lambda message: message.text == 'fTfG_Ah`A2BlV{Z' or message.text == '12344321' or message.text == 'qwerty1234' or message.text == 'Yandex228')
def result(message):
    global d
    chat_id = message.chat.id
    global id
    if message.text =="fTfG_Ah`A2BlV{Z":
        d += 1
    else:
        d += 0
    conn = sqlite3.connect('tg.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(f'INSERT INTO answer VALUES (?, ?)', (id, d))#внесение в данных в таблицу
    conn.commit()#сохранение данных
    cursor.close()
    conn.close()
    bot.send_message(message.chat.id, f"Ваш результат: {d}/5")#вывод результата
    d = 0

bot.infinity_polling()