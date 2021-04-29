import telebot
import sqlite3


def post_sql_query(sql_query=""):
    with sqlite3.connect('telegram_bot.db') as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(sql_query)
        except sqlite3.Error:
            pass
        result = cursor.fetchall()
        connection.commit()
        return result


def get_table(name):
    return post_sql_query('SELECT * FROM ' + name + ';')


def create_table():
    users_query = '''CREATE TABLE IF NOT EXISTS users(
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT);'''
    post_sql_query(users_query)


def create_admins():
    admins_query = '''CREATE TABLE IF NOT EXISTS admins(
                        userid TEXT PRIMARY KEY
                        );'''
    post_sql_query(admins_query)
    post_sql_query('INSERT or IGNORE INTO admins (userid) VALUES ("sky1ark");')


def register_user(first_name, last_name, email):
    insert_to_db_query = f'INSERT INTO users (first_name,  last_name, email) VALUES ("{first_name}", "{last_name}", "{email}");'
    post_sql_query(insert_to_db_query)


def add_admin(username):
    print('add_admin', username)
    post_sql_query(f'INSERT or IGNORE INTO admins (userid) VALUES ("{username}");')


def delete_admin_from_sql(username):
    print('delete_admin_from_sql', username)
    post_sql_query(f'DELETE FROM admins WHERE userid = "{username}";')


bot = telebot.TeleBot('1743771772:AAHjwPGP2zXilKE1O1d0BwNtjqpP6jjr97k')

create_table()
create_admins()


def is_admin(username):
    for i in get_table("admins"):
        if username == i[0]:
            return True
    return False


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.from_user.id, 'Для регистрации напишите /reg')


class userData:
    user_id = ""
    user_name = ""
    first_name = ""
    last_name = ""
    email = ""


data = userData()


@bot.message_handler(commands=['reg'])
def register(message):
    print('register', message.from_user.username)
    bot.send_message(message.from_user.id, 'Введите ваше имя')
    bot.register_next_step_handler(message, get_first_name)


@bot.message_handler(commands=['add_admin'])
def register_admin(message):
    print('add_admin', message.from_user.username)
    if is_admin(message.from_user.username):
        bot.send_message(message.from_user.id, 'Введите username')
        bot.register_next_step_handler(message, register_admin)
    else:
        bot.send_message(message.from_user.id, 'У вас не прав для этого действия.')


@bot.message_handler(commands=['delete_admin'])
def delete_admin(message):
    print('delete_admin', message.from_user.username)
    if is_admin(message.from_user.username):
        bot.send_message(message.from_user.id, 'Введите username')
        bot.register_next_step_handler(message, deleter_admin)
    else:
        bot.send_message(message.from_user.id, 'У вас не прав для этого действия.')


@bot.message_handler(commands=['show_info'])
def show_info(message):
    print('show_info', message.from_user.username)
    username = message.from_user.username
    if is_admin(username):
        report = "Все зарегистрированные пользователи:\n"
        for j in get_table("users"):
            report += ', '.join(j)
            report += '\n'
        bot.send_message(message.from_user.id, report)
    else:
        bot.send_message(message.from_user.id, "У вас нет прав для этого действия")


@bot.message_handler(commands=['show_admins'])
def show_admins(message):
    print('show_admins', message.from_user.username)
    username = message.from_user.username
    if is_admin(username):
        report = "Все администраторы:\n"
        for j in get_table("admins"):
            report += ', '.join(j)
            report += '\n'
        bot.send_message(message.from_user.id, report)
    else:
        bot.send_message(message.from_user.id, "У вас нет прав для этого действия")


@bot.message_handler(content_types=['text'])
def register_admin(message):
    print('register_admin', message.from_user.username, message.text)
    add_admin(message.text)


@bot.message_handler(content_types=['text'])
def deleter_admin(message):
    print('deleter_admin', message.from_user.username, message.text)
    delete_admin_from_sql(message.text)


@bot.message_handler(content_types=['text'])
def get_first_name(message):
    print('get_first_name', message.from_user.username, message.text)
    data.first_name = message.text
    bot.send_message(message.from_user.id, 'Введите вашу фамилию')
    bot.register_next_step_handler(message, get_last_name)


@bot.message_handler(content_types=['text'])
def get_last_name(message):
    print('get_last_name', message.from_user.username, message.text)
    data.last_name = message.text
    bot.send_message(message.from_user.id, 'Введите ваш адрес электронной почты')
    bot.register_next_step_handler(message, get_email)


@bot.message_handler(content_types=['text'])
def get_email(message):
    print('get_email', message.from_user.username, message.text)
    data.email = message.text
    register_user(data.first_name, data.last_name, data.email)
    bot.send_message(message.from_user.id, 'Вы успешно зарегистрированы!')


bot.polling(none_stop=True, interval=0.5)
