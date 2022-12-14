import psycopg2
from config import host, user, password, db_name
from datetime import datetime
import parser_test
import answers


class BotDataBase:
    def __init__(self):
        try:
            self.connection = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                database=db_name
            )
            self.cursor = self.connection.cursor()
        except Exception as _ex:
            print("[ERROR]", _ex)

    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def db_add_users(self, id_tg, username_tg):
        print("YES")
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                            (id_tg, date, "@" + username_tg))
        self.connection.commit()

    def __db_add_articles(self, id_article):
        # проверка наличия артикула в таблице
        if not self.cursor.execute("SELECT EXISTS (SELECT %s FROM articles WHERE id_article = %s)",
                                   (1, id_article)):
            # получение информации об артикуле
            pars_result = parser_test.check(id_article)
            price = pars_result[0]
            name = pars_result[1]
            # добавление артикула в таблицу
            self.cursor.execute("INSERT INTO articles VALUES (%s, %s, %s, %s)", (id_article, price, True, name))
        self.connection.commit()

    def __db_articles_update(self, id_article, price, active, name):
        # добавление артикула в историю
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO articles_history"
                            "(SELECT id_article, price, %s as date, name "
                            "FROM articles WHERE id_article = %s)",
                            (date, id_article))
        self.connection.commit()

        # обновление информации об артикуле
        self.cursor.execute("SELECT price, active, name FROM articles WHERE id_article = %s", (id_article,))
        article_info = self.cursor.fetchone()

        # словари значений артикула
        article_main = {
            "price": article_info[0],
            "active": article_info[1],
            "name": "'" + str(article_info[2]) + "'"
        }

        article_sub = {
            "price": price,
            "active": active,
            "name": "'" + name + "'"
        }

        # создание уникального словаря, article_update = article_sub ССЫЛКИ ОДИНАКОВЫЕ
        article_update = article_sub.copy()

        for elem in article_sub:
            if article_sub[elem] != article_main[elem]:
                article_update[elem] = article_sub[elem]
            else:
                article_update.pop(elem)

        # обновление значений артикула
        if article_update:
            for column in article_update:
                self.cursor.execute("UPDATE {} SET {} = {} WHERE id_article = {}"
                                    .format('articles', column, article_update[column], id_article))
        self.connection.commit()

    def db_add_favorite_articles(self, id_tg, id_article):
        # Проверка существования записи
        if not self.cursor.execute("SELECT EXISTS (SELECT %s FROM favorite_articles "
                                   "WHERE (id_tg = %s AND id_article = %s))",
                                   (1, id_tg, id_article)):
            # Добавление артикула в общий список
            self.__db_add_articles(id_article)
            # Добавление артикула к избранным
            self.cursor.execute("INSERT INTO favorite_articles VALUES (%s, %s)",
                                (id_tg, id_article))
            self.connection.commit()

            # Добавление в историю
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.__db_add_favorites_history(id_tg, id_article, True, date)

    def db_remove_favorite_articles(self, id_tg, id_article):
        # Проверка существования записи
        if self.cursor.execute("SELECT EXISTS (SELECT %s FROM favorite_articles "
                               "WHERE (id_tg = %s AND id_article = %s))",
                               (1, id_tg, id_article)):
            # удаление записи из favorite_articles
            self.cursor.execute("DELETE FROM favorite_articles WHERE id_tg = %s AND id_article = %s RETURNING *",
                                (id_tg, id_article))

            # добавление записи в историю
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            answer = answers.del_successful
            action = False
            self.__db_add_favorites_history(id_tg, id_article, action, date)

            # Проверка наличия артикула у других пользователей и выбор active для артикула в articles
        if not self.cursor.execute("SELECT EXISTS (SELECT %s FROM favorite_articles WHERE id_article = %s)",
                                   (1, id_article)):
            self.cursor.execute("UPDATE articles SET active = %s", (False,))
        self.connection.commit()

    def __db_add_favorites_history(self, id_tg, id_article, action, date):
        self.cursor.execute("INSERT INTO favorites_history VALUES (%s, %s, %s, %s)", (id_tg, id_article, action, date))
        self.connection.commit()

    def db_show_favorite_articles(self, id_tg):
        self.cursor.execute("SELECT id_article, price FROM articles WHERE id_article IN"
                            "(SELECT id_article FROM favorite_articles WHERE id_tg = %s)", (id_tg,))
        result = self.cursor.fetchall()
        answer = ''
        for row in result:
            answer += (f'Артикул {row[0]}, '
                  f'цена {row[1]}\n')
        print(answer)
        self.connection.commit()

    def db_articles_price_update(self):
        # Сбор активных артикулов
        self.cursor.execute("SELECT id_article FROM articles WHERE active = %s",
                            (True,))
        active_articles = self.cursor.fetchall()
        self.connection.commit()

        id_articles = []
        for id_ in active_articles:
            id_articles.append(id_[0])

        # Получение новых данных
        pars_result = parser_test.pars_articles(id_articles)

        # Обновление артикулов в таблице
        for id_article, article_info in pars_result.items():
            for name in article_info:
                price = article_info[name]
                self.__db_articles_update(id_article, price, True, name)
                self.connection.commit()


if __name__ == '__main__':
    DB = BotDataBase()
    DB.db_add_favorite_articles(329202821, 13757736)
    #DB.db_articles_price_update()
    #DB.db_show_favorite_articles(329202821)
    #DB.db_add_favorite_articles(329202821, 1)
    # DB.db_articles_update(1, 656, False, '11Item21')
    # DB.db_articles_price_update()
    # При добавлении артикула ставить ему True если он уже был!!
