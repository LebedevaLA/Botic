import sqlite3 as sql
import random


class DataTable:

    def __init__(self, con):
        self.connection = sql.connect(con, check_same_thread=False)
        self.cur = self.connection.cursor()

    def create_tables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS to_do_table (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT NOT NULL
                )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS photos (
                     id_photo INTEGER PRIMARY KEY ,
                     path TEXT NOT NULL,
                     id_name INTEGER,
                     FOREIGN KEY (id_name)  REFERENCES to_do_table(id)
                )""")

        self.connection.commit()

    def add_name(self, name):
        self.cur.execute('SELECT COUNT(*) FROM to_do_table WHERE to_do_table.name=?', (name,))
        count = self.cur.fetchone()[0]
        if count == 0:
            self.cur.execute('INSERT into to_do_table(name) VALUES(?)', (name,))
            self.connection.commit()
            return 'Сделано!'
        else:
            return 'Такое занятие уже есть в таблице'

    def find_this_path(self, path):
        self.cur.execute('SELECT path FROM photos')
        paths = self.cur.fetchall()
        for url in paths:
            if url[0] == path:
                return True
        return False

    #за это тоже извините
    def find_pathend(self,path_end):
        self.cur.execute('SELECT path FROM photos')
        paths = self.cur.fetchall()
        for i in range(0,len(paths)):
            url = paths[i]
            for j in range(0,len(url)):
                end = url[j].split('/')
                if end[len(end)-1] == path_end:
                    return url
        return ''

    def search_name(self, name):
        self.cur.execute('SELECT id FROM to_do_table WHERE to_do_table.name=?', (name,))
        id_name = self.cur.fetchall()
        if not id_name:
            return 'Такого занятия ещё нет в таблице, нужно его добавить'
        else:
            return id_name[0][0]

    def add_photo(self, id_name, path):
        try:
            open(path, 'rb')
        except FileNotFoundError:
            return 'Упс,нужно проверить корректность пути к файлу'
        else:
            if not self.find_this_path(path):
                self.cur.execute('INSERT into photos(path,id_name) VALUES(?,?)', (path, id_name,))
                self.connection.commit()
                return 'Сделано!'
            else:
                return "Это фото уже добавили"

    def get(self):
        self.cur.execute('SELECT id FROM to_do_table')
        lower_bound = self.cur.fetchone()
        if not lower_bound:
            return ''
        else:
            self.cur.execute('SELECT COUNT(*) FROM to_do_table')
            upper_bound = self.cur.fetchone()[0] + lower_bound[0]
            rand = random.randint(lower_bound[0], upper_bound-1)
            message = ''
            self.cur.execute('SELECT path FROM photos,to_do_table WHERE to_do_table.id=? AND to_do_table.id=photos.id_name', (rand,))
            table = self.cur.fetchall()
            if not table:
                return "Для этого занятия ещё нет фото("
            else:
                self.cur.execute('SELECT name FROM to_do_table WHERE to_do_table.id=?', (rand,))
                title = self.cur.fetchall()
                message += title[0][0]
                for path in table:
                    message += '\n' + path[0]
                return message

    def get_all_names(self):
        self.cur.execute('SELECT name FROM to_do_table')
        table = self.cur.fetchall()
        message=''
        if not table:
            return message
        for name in table:
            message += name[0]+'\n'
        return message[:-1]

    def get_name_photos(self,id_name):
        self.cur.execute('SELECT path FROM photos WHERE photos.id_name=?', (id_name,))
        urls = self.cur.fetchall()
        if not urls:
            return ''
        message=''
        for url in urls:
            message += url[0]+'\n'
        return message[:-1]

    def get_all_photos(self):
        self.cur.execute('SELECT * FROM photos')
        table = self.cur.fetchall()
        for url in table:
            print(url)

    def delete_photo(self, path_end):
        path = self.find_pathend(path_end)
        if path != '':
            self.cur.execute('DELETE FROM photos WHERE photos.path=?', (path[0],))
            self.connection.commit()
            return 'Запись удалена'
        else:
            return 'Упс, что-то пошло не так'

    def delete_name(self, name):
        self.cur.execute('SELECT id FROM to_do_table WHERE name=?', (name,))
        id = self.cur.fetchall()
        self.cur.execute('DELETE FROM to_do_table WHERE name=?', (name,))
        self.connection.commit()
        self.cur.execute('SELECT COUNT(*) FROM photos WHERE photos.id_name=?', (id[0][0],))
        count = self.cur.fetchone()[0]
        if count != 0:
            self.cur.execute('DELETE FROM photos WHERE id_name=?', (id[0][0],))
            self.connection.commit()
        return 'Запись удалена'

    def delete_all_records(self):
        self.cur.execute('DELETE FROM to_do_table')
        self.connection.commit()
        self.cur.execute('DELETE FROM photos')
        self.connection.commit()

    def delete_all_photos(self):
        self.cur.execute('DELETE FROM photos')
        self.connection.commit()

    def end(self):
        self.cur.close()
        self.connection.close()