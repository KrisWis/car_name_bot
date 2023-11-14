import psycopg2

with psycopg2.connect(dbname="postgres", user="postgres", password="1234", host="127.0.0.1") as db:
    cursor = db.cursor()

    def check_db():
        try:
            cursor.execute("SELECT * FROM cars")
            print("Таблица cars запущена")

        except:
            db.rollback()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS cars (
                            id SERIAL PRIMARY KEY,
                            car_number TEXT,
                            subscribe_users TEXT ARRAY,
                            owner_username TEXT,
                            interested_users TEXT ARRAY)
                            """
            )
            print("Таблица cars создана")

        try:
            cursor.execute("SELECT * FROM users")
            print("Таблица users запущена")

        except:
            db.rollback()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            user_id BIGINT NOT NULL,
                            subscribe_car_numbers TEXT ARRAY,
                            history BIGINT ARRAY,
                            balance INTEGER DEFAULT (0),
                            ref_id BIGINT,
                            ban INTEGER DEFAULT (0))
                            """
            )
            print("Таблица users создана")

        try:
            cursor.execute("SELECT * FROM reports")
            print("Таблица reports запущена")

        except:
            db.rollback()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS reports (
                            id SERIAL PRIMARY KEY,
                            report_id BIGINT NOT NULL,
                            car_number TEXT,
                            car_text TEXT,
                            car_photo TEXT,
                            car_owner_username TEXT,
                            author_id BIGINT NOT NULL)
                            """
            )
            print("Таблица reports создана")

        try:
            cursor.execute("SELECT * FROM setting")
            print("Таблица setting запущена")

        except:
            db.rollback()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS setting (
                            id SERIAL PRIMARY KEY,
                            report_amount BIGINT DEFAULT (0),
                            owner_amount BIGINT DEFAULT (0),
                            ref_percent BIGINT DEFAULT (0))
                            """
            )

            cursor.execute('INSERT INTO setting (id) VALUES (1)')

            print("Таблица setting создана")

        db.commit()

    def user_exists(user_id):

        cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (user_id,))

        if not cursor.fetchone():
            return False

        return True


    def add_user(user_id, ref_id=None):

        cursor.execute('''INSERT INTO users (
                          user_id,
                          ref_id,
                          subscribe_car_numbers,
                          history)
                          VALUES (%s, %s, %s, %s)
                          ''',
                       (user_id, ref_id, [], []))

        db.commit()

    # Функция для подписки пользователя на уведомления по номеру машины
    def subscribe_user_for_car_number(car_number, user_id):

        if not car_exists(car_number):
            cursor.execute(
                """INSERT INTO cars (car_number, subscribe_users, owner_username, interested_users)
                            VALUES (%s, %s, %s, %s, %s)""",
                (car_number, [], [], "", []),
            )

        else:
            cursor.execute(
                "SELECT subscribe_users FROM cars WHERE car_number = %s", (car_number,)
            )
            existing_subscribe_users = cursor.fetchone()[0]

            if str(user_id) not in existing_subscribe_users:
                existing_subscribe_users.append(user_id)

            cursor.execute(
                "UPDATE cars SET subscribe_users = %s WHERE car_number = %s",
                (existing_subscribe_users, car_number),
            )

        db.commit()

    # Функция для добавления владельца машины
    def add_owner_username(car_number, username):

        cursor.execute(
            "UPDATE cars SET owner_username = %s WHERE car_number = %s",
            (username, car_number),
        )

        cursor.execute(
            "UPDATE reports SET car_owner_username = %s WHERE car_number = %s",
            (username, car_number),
        )

        db.commit()


    def car_exists(car_number):

        cursor.execute(
            "SELECT car_number FROM cars WHERE car_number = %s", (car_number,)
        )

        if not cursor.fetchone():
            return False

        return True

    def owner_exists(car_number):

        cursor.execute(
            "SELECT owner_username FROM cars WHERE car_number = %s", (car_number,)
        )

        exists = cursor.fetchone()

        if not exists:
            return False
        else:
            if exists[0]:
                return True
            
            return False
    
    # Функция для получения информации о пользователе
    def get_info_user(user_id):
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))

        return cursor.fetchone()

    # Функция для добавления подписки на уведомления на номер для пользователя
    def add_subscribe_number(user_id, subscribe_car_number):
        existing_subcribe_numbers = get_info_user(user_id)[2]

        if str(subscribe_car_number) not in existing_subcribe_numbers:
            existing_subcribe_numbers.append(subscribe_car_number)

        cursor.execute(
            "UPDATE users SET subscribe_car_numbers = %s WHERE user_id = %s",
            (existing_subcribe_numbers, user_id),
        )
        db.commit()

    # Функция для добавления отчёта в историю пользователя
    def add_report_to_history(user_id, report_id):

        existing_history = get_info_user(user_id)[3]
        existing_history.append(int(report_id))

        cursor.execute('UPDATE users SET history = %s  WHERE user_id = %s', ([], user_id,))

        cursor.execute('UPDATE users SET history = %s WHERE user_id = %s', (existing_history, user_id),)

        db.commit()

    # Функция для пополнения/списывания баланса пользователя. Чтобы списать деньги просто отправь отрицательное число в параметр amount.
    def change_balance(user_id, amount):
        user_balance = get_info_user(user_id)[4]
        user_balance += amount

        cursor.execute(
            "UPDATE users SET balance = %s WHERE user_id = %s", (user_balance, user_id)
        )
        db.commit()

    # Функция для выдавания текущего баланса пользователя (можно было не делать, т.к одна строчка кода, но решил оставить)
    def get_balance(user_id):
        return get_info_user(user_id)[4]

    # Функция для выдавания истории пользователя (можно было не делать, т.к одна строчка кода, но решил оставить)
    def get_history(user_id):
        return get_info_user(user_id)[3]

    # Функция для выдавания номеров машин, на уведомления по которым, подписан пользователь (можно было не делать, т.к одна строчка кода, но решил оставить)
    def get_subscribe_car_numbers(user_id):
        return get_info_user(user_id)[2]

    # Функция для выдавания описания машины по её номеру
    def get_car_desc(car_number):
        cursor.execute("SELECT car_desc FROM cars WHERE car_number = %s", (car_number,))
        car_desc = cursor.fetchone()

        if car_desc is None:
            return False
        else:
            return car_desc[0]

    # Функция для выдавания владельца машины
    def get_car_owner_username(car_number):
        cursor.execute(
            "SELECT owner_username FROM cars WHERE car_number = %s", (car_number,)
        )
        owner_username = cursor.fetchone()

        if owner_username is None:
            return False
        else:
            return owner_username[0]

    # Функция для выдавания подписанных на уведомления пользователей по номеру машины
    def get_car_subscribe_users(car_number):
        cursor.execute(
            "SELECT subscribe_users FROM cars WHERE car_number = %s", (car_number,)
        )
        subscribe_users = cursor.fetchone()

        if subscribe_users is None:
            return []
        else:
            return subscribe_users[0]

    # Функция для добавления отчёта
    def add_car_report(report_id, car_number, car_text, author_id, car_photo=None, car_owner_username=None):
        cursor.execute(
            "SELECT report_id FROM reports WHERE report_id = %s", (report_id,)
        )

        if cursor.fetchone() is None:  # Проверка на то, что такого ID в базе нет
            cursor.execute(
                """INSERT INTO reports (report_id, car_number, car_text, car_photo, car_owner_username, author_id)
                            VALUES (%s, %s, %s, %s, %s, %s)""",
                (report_id, car_number, car_text, car_photo, car_owner_username, author_id))

            db.commit()

    # Функция для выдавания данных об отчёте по его ID
    def get_report_info(report_id):

        cursor.execute("SELECT * FROM reports WHERE report_id = %s", (report_id,))

        return cursor.fetchone()

    # Функция для выдачи всех отчётов по номеру машины
    def get_car_number_reports(car_number):

        cursor.execute("SELECT * FROM reports WHERE car_number = %s", (car_number,))

        return cursor.fetchall()


    def get_ref(user_id):

        cursor.execute('SELECT user_id FROM users WHERE ref_id = %s', (user_id,))

        return cursor.fetchall()


    def get_setting():

        cursor.execute('SELECT * FROM setting')

        return cursor.fetchone()


    def update_setting(row, value):

        cursor.execute(f'UPDATE setting SET {row} = %s', (value,))

        db.commit()

    def get_users():

        cursor.execute('SELECT user_id FROM users')

        return cursor.fetchall()

    def ban_user(user_id, value):

        cursor.execute('UPDATE users SET ban = %s WHERE user_id = %s', (value, user_id,))

        db.commit()

    # Функция для добавления юзера в массив интересовавшихся юзеров
    def add_interested_user(car_number, user_id):

        if not car_exists(car_number):
            cursor.execute(
                """INSERT INTO cars (car_number, subscribe_users, owner_username, interested_users)
                            VALUES (%s, %s, %s, %s)""",
                (car_number, [], "", []),
            )
        
        cursor.execute(
            "SELECT interested_users FROM cars WHERE car_number = %s", (car_number,)
        )

        existing_interested_users = cursor.fetchone()
        if existing_interested_users:
            existing_interested_users = existing_interested_users[0]
        else:
            existing_interested_users = []

        if str(user_id) not in existing_interested_users:
            existing_interested_users.append(user_id)

        cursor.execute(
            "UPDATE cars SET interested_users = %s WHERE car_number = %s",
            (existing_interested_users, car_number),
        )

        db.commit()

    # Функция для получения количества интересовавшихся номером пользователей
    def get_interested_users_amount(car_number):
        cursor.execute(
            "SELECT interested_users FROM cars WHERE car_number = %s", (car_number,)
        )

        existing_interested_users = cursor.fetchone()

        if existing_interested_users:
            return len(existing_interested_users[0])
        else:
            return 0