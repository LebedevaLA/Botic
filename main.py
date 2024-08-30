import telebot
import datetime
import schedule
from SQLdata import DataTable
from GoodleCalendar import GoogleCalendar
from telebot.types import InputMediaPhoto
from telebot import types
import time
import threading
from configparser import ConfigParser


urlsconf ='for_bot.ini'
config = ConfigParser()
config.read(urlsconf)
bot = telebot.TeleBot(config['TEL_BOT']['api'])
obj = GoogleCalendar()
calendar = 'alldifferent.6489@gmail.com'
obj.add_calendar(calendar)


def remind():
    date1 = datetime.datetime.now()
    if date1.hour > 0 and date1.hour < 5:
        today_date = datetime.date.today()
        message1 = get_event(today_date)
    else:
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        message1 = get_event(tomorrow_date)
    bot.send_message(chat_id =config['TEL_BOT']['chat_id'] , text = message1)


def foo():
    schedule.every().day.at("02:23").do(remind)
    while True:
        schedule.run_pending()
        time.sleep(1)


def get_event(date):
    events = obj.service.events().list(
        calendarId=calendar,
        timeMin=date.isoformat() + 'T00:00:00Z',
        timeMax=date.isoformat() + 'T23:59:59Z',
        singleEvents=True,
        orderBy='startTime',
    ).execute()
    message1 = ''
    for event in events['items']:
        start_str = event['start'].get('dateTime')
        start_in_datetime = datetime.datetime.fromisoformat(start_str)
        end_str = event['end'].get('dateTime')
        end_in_datetime = datetime.datetime.fromisoformat(end_str)
        message1 += event['summary'] + '  ' + \
                    f'{start_in_datetime.hour:02} : {start_in_datetime.minute:02} ' + '-' \
                    + f' {end_in_datetime.hour:02} : {end_in_datetime.minute:02}' + '\n'
        if event.get('description') != None:
            message1 += event.get('description')
    if message1 == '':
        message1 = 'Нет запланированных событий'
    return message1


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}!\n'
                                      'С помощью этого бота ты cможешь посмотреть своё расписание'
                                      ' и возможно даже найти новое хобби)'
    )


@bot.message_handler(commands=['to_do_today'])
def today(message):
    today_date = datetime.date.today()
    message1 = get_event(today_date)
    bot.send_message(message.chat.id, message1)


@bot.message_handler(commands=['to_do_tomorrow'])
def tomorrow(message):
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    message1 = get_event(tomorrow_date)
    bot.send_message(message.chat.id, message1)


@bot.message_handler(commands=['admin'])
def admin(message):
    buttons = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text="Добавить запись", callback_data="add")
    btn2 = types.InlineKeyboardButton(text="Удалить запись", callback_data="del")
    btn3 = types.InlineKeyboardButton(text="Выйти", callback_data="end")
    buttons.add(btn1, btn2,btn3)
    bot.send_message(message.chat.id,
                     text="Вы зашли в админку для добавления и удаления занятий и фото к ним".format(
                         message.from_user), reply_markup=buttons)


done = []
data = DataTable('Data_for_bot')


#простите за это(
@bot.callback_query_handler(func=lambda c:True)
def ans(c):

    buttons = types.InlineKeyboardMarkup()
    chat_id = c.message.chat.id
    if c.data == "add":
        btn1 = types.InlineKeyboardButton(text="Добавить название занятия", callback_data="add_n")
        btn2 = types.InlineKeyboardButton(text="Добавить фото к занятию", callback_data="add_p")
        btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
        buttons.add(btn1, btn2, btn3)
        bot.send_message(chat_id,
                         text="Выберите действие".format(
                             c.message.from_user), reply_markup=buttons)

    elif c.data == "end":
        bot.send_message(chat_id, 'Вы вышли')
        bot.clear_step_handler_by_chat_id(chat_id)

    elif c.data == "del":
        btn1 = types.InlineKeyboardButton(text="Удалить занятие", callback_data="del_n")
        btn2 = types.InlineKeyboardButton(text="Удалить фото", callback_data="del_p")
        btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
        buttons.add(btn1, btn2, btn3)
        bot.send_message(chat_id,
                         text="Выберите, действие".format(
                             c.message.from_user), reply_markup=buttons)

    elif c.data == "add_n":
        name = bot.send_message(chat_id, 'Введите название занятия')
        bot.register_next_step_handler(name, add_name)
        done.append("add_n")

    elif c.data == "add_p":
        mes = data.get_all_names()
        if mes == '':
            bot.send_message(chat_id, 'В списке занятий пусто')
        else:
            all_names = mes.split('\n')
            for i in range(0, len(all_names)):
                btn = types.InlineKeyboardButton(text=all_names[i], callback_data=all_names[i])
                buttons.add(btn)
            btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
            buttons.add(btn3)
            bot.send_message(chat_id,
                             text="Выберите название занятия".format(
                                 c.message.from_user), reply_markup=buttons)

            done.append('add_p')

    elif len(done) != 0 and done[len(done)-1] == 'add_p':
        url = bot.send_message(chat_id, 'Введите путь к фото на вашем пк')
        id_ = data.search_name(c.data)
        bot.register_next_step_handler(url, add_photo, id_)

    elif c.data == "del_n":
        mes = data.get_all_names()
        if mes == '':
            bot.send_message(chat_id, 'В списке занятий пусто')
        else:
            all_names = mes.split('\n')
            for i in range(0, len(all_names)):
                btn = types.InlineKeyboardButton(text=all_names[i], callback_data=all_names[i])
                buttons.add(btn)
            btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
            buttons.add(btn3)
            bot.send_message(chat_id,
                             text="Выберите название занятия".format(
                                 c.message.from_user), reply_markup=buttons)
            done.append('del_n')

    elif len(done) != 0 and done[len(done)-1] == 'del_n':
        bot.send_message(chat_id, data.delete_name(c.data))

    elif c.data == 'del_p':
        mes = data.get_all_names()
        if mes == '':
            bot.send_message(chat_id, 'В списке занятий пусто')
        else:
            all_names = mes.split('\n')
            for i in range(0, len(all_names)):
                btn = types.InlineKeyboardButton(text=all_names[i], callback_data=all_names[i])
                buttons.add(btn)
            btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
            buttons.add(btn3)
            bot.send_message(chat_id,
                             text="Выберите название занятия".format(
                                 c.message.from_user), reply_markup=buttons)
            done.append('del_p')

    elif len(done) != 0 and done[len(done)-1] == 'del_p':
        id_ = data.search_name(c.data)
        mes = data.get_name_photos(id_)
        if mes == '':
            bot.send_message(chat_id, 'В списке фото для этого занятия пусто')
        else:
            all_urls = mes.split('\n')
            for i in range(0, len(all_urls)):
                parse = all_urls[i].split('/')
                btn1 = types.InlineKeyboardButton(text=parse[len(parse)-1], callback_data=parse[len(parse)-1])
                buttons.add(btn1)
            btn3 = types.InlineKeyboardButton(text="Выйти из админки", callback_data="end")
            buttons.add(btn3)
            bot.send_message(chat_id,
                             text="Что удаляем? ".format(
                                 c.message.from_user), reply_markup=buttons)
            done.append('del_p1')

    elif len(done) != 0 and done[len(done)-1] == 'del_p1':
        bot.send_message(chat_id, data.delete_photo(c.data))


def add_photo(url, id_):
    bot.send_message(url.chat.id, data.add_photo(id_, url.text))


def add_name(message):
    data.create_tables()
    bot.send_message(message.chat.id, data.add_name(message.text))
    data.end()


@bot.message_handler(commands=['random_thing_to_do'])
def random(message):
    data = DataTable('Data_for_bot')
    mes = data.get()
    if mes == '':
        bot.send_message(message.chat.id,"Упс, кажется база данных потерялась или оказалась пустой")
    else:
        list=mes.split('\n')
        bot.send_message(message.chat.id, mes.split('\n')[0])
        all_photos=[]
        for i in range(1, len(list)):
            photo = open(list[i], 'rb')
            mediaPhoto = InputMediaPhoto(photo)
            all_photos.append(mediaPhoto)
        bot.send_media_group(message.chat.id, all_photos)
    data.end()


if __name__ == '__main__':
    thread = threading.Thread(target=foo)
    thread.start()
    bot.polling(none_stop=True)

