from InstanceBot import bot, yoomoney_client
from aiogram import types, Dispatcher
from keyboards import Keyboards
from aiogram.dispatcher import FSMContext
from database import db
from yoomoney import Quickpay
import random
import Config
from states import User


async def start(msg: types.Message, state: FSMContext):
    user_id = msg.from_user.id
    username = msg.from_user.username
    start_message = msg.text[7:]

    if not db.user_exists(user_id):

        if len(start_message) > 0 and not start_message.startswith("c"):
            if start_message.isdigit() and start_message != str(user_id):

                db.add_user(user_id, ref_id=start_message)

                await bot.send_message(
                    chat_id=start_message,
                    text=f'У Вас новый реферал @{username}!'
                )
        else:
            if start_message.startswith("c"):
                if start_message != str(user_id):
                    referrer_id = start_message.split("_")[2]

                    db.add_user(user_id, ref_id=referrer_id)

                    await bot.send_message(
                        chat_id=referrer_id,
                        text=f'У Вас новый реферал @{username}!'
                    )

            else:
                db.add_user(user_id)

        await bot.send_message(
            chat_id=Config.admin_id[0],
            text='Новый пользователь!\n'
                 f'ID: {user_id}\n'
                 f'Username: @{msg.from_user.username}'
        )

    if db.get_info_user(user_id)[6] == 1:
        return
    
    if start_message.startswith("c"):
        car_number = start_message.split("_")[1]
        msg.text = car_number
        await add_car_report_button(msg, state)
    else:
        await User.menu.start.set()
        await msg.answer("""ДОБРО ПОЖАЛОВАТЬ🎈
➖➖➖➖➖➖➖➖➖➖➖➖➖
Бот покажет что пишут о вас другие люди!
Посмотрите, может о вас уже написали👨‍💻 
Поиск осуществляется по «Госномеру», «Номеру телефона» или «VIN-коду». 
➖➖➖➖➖➖➖➖➖➖➖➖➖
Выберите нужное действие:""", reply_markup=Keyboards.menu())


async def add_car_report_button(msg: types.Message, state: FSMContext):
    car_number = msg.text
    car_owner_username = db.get_car_owner_username(car_number)
    bot_name = await bot.get_me()
    user_id = msg.from_user.id
    interested_users_amount = db.get_interested_users_amount(car_number)

    await state.update_data(car_number=car_number)

    db.add_interested_user(car_number, user_id)

    await User.menu.start.set()
    if not db.get_car_number_reports(car_number):

        await state.update_data(first_report_bool=True)

        await msg.answer(
            "Не найдено комментариев"
            + f"\nЭтим номером интересовались {interested_users_amount} человек."
            + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}",
            reply_markup=Keyboards.add_own_car_report(),
        )

    else:
        await state.update_data(first_report_bool=False)
        reports_amount = len(db.get_car_number_reports(car_number))

        await msg.answer(
            (f"Найдено {reports_amount} комментариев"
            if not car_owner_username
            else f"Найдено {reports_amount} комментариев. Владелец найден.")
            + f"\nЭтим номером интересовались {interested_users_amount} человек."
            + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}",
            reply_markup=Keyboards.add_or_see_report(car_number),
        )


async def see_car_report_button(msg: types.Message, state: FSMContext):
    car_number = msg.text
    car_owner_username = db.get_car_owner_username(car_number)
    bot_name = await bot.get_me()
    user_id = msg.from_user.id
    interested_users_amount = db.get_interested_users_amount(car_number)

    await state.update_data(car_number=car_number)

    db.add_interested_user(car_number, user_id)

    await User.menu.start.set()
    if not db.get_car_number_reports(car_number):
        await msg.answer(
            "Не найдено комментариев"
            + f"\nЭтим номером интересовались {interested_users_amount} человек."
            + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}"
        )

    else:
        reports_amount = len(db.get_car_number_reports(car_number))

        await msg.answer(
            (f"Найдено {reports_amount} комментариев"
            if not car_owner_username
            else f"Найдено {reports_amount} комментариев. Владелец найден.")
            + f"\nЭтим номером интересовались {interested_users_amount} человек."
            + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}",
            reply_markup=Keyboards.see_report(car_number),
        )


async def replenish_balance(msg: types.Message, state: FSMContext):

    if not msg.text.isdigit():
        await msg.answer('Введите число!')
        return

    balance_replenish_amount = int(msg.text)
    user_id = msg.from_user.id
    random_label = random.randint(0, 1000)

    await state.update_data(balance_replenish_amount=balance_replenish_amount)
    await state.update_data(random_label=random_label)

    user = yoomoney_client.account_info()

    quickpay = Quickpay(
        receiver=user.account,
        quickpay_form="shop",
        targets="paying for report",
        paymentType="SB",
        sum=balance_replenish_amount,
        label=f"{user_id}__{random_label}",
    )

    await User.menu.start.set()
    await msg.answer(
        f"Для пополнения баланса на {balance_replenish_amount} монет, перейди по ссылке - {quickpay.base_url}",
        reply_markup=Keyboards.check_payment(),
    )


async def add_own_car_report(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    user_car_number = data["car_number"]
    user_id = msg.from_user.id

    if msg.photo:
        user_photo = msg.photo[-1].file_id
        user_text = msg.caption

        await bot.send_photo(
            Config.admin_id[0],
            photo=user_photo,
            caption=f'Комментарий пользователя по номеру "{user_car_number}": \n{user_text}',
            reply_markup=Keyboards.approve_or_reject_report(user_id, user_car_number),
        )
    else:
        user_text = msg.text

        await bot.send_message(
            Config.admin_id[0],
            f'Комментарий пользователя по номеру "{user_car_number}": \n{user_text}',
            reply_markup=Keyboards.approve_or_reject_report(user_id, user_car_number),
        )

    await User.menu.start.set()
    await msg.answer("Ваш комментарий отправлен на модерацию! Вам придёт уведомление.", reply_markup=Keyboards.menu())


async def callback_query_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    username = call.from_user.username

    if db.get_info_user(user_id)[6] == 1:
        return

    await bot.answer_callback_query(
        callback_query_id=call.id,
        text='✅'
    )

    if call.data == "add_car_report_button":
        await call.message.edit_text("Введите запрос в формате «х111хх777» или «79991112233»")

        await User.UserState.add_car_report_button.set()

    elif call.data == "add_own_car_report":
        await call.message.edit_text("Введите текст, так же можно 1 фото. После модерации ваш комментарий будет доступен для всех.")

        await User.UserState.add_own_car_report.set()

    elif call.data.startswith("report_approve"):
        user_id = call.data.split("__")[1]
        car_number = call.data.split("__")[2]
        subscribed_users = db.get_car_subscribe_users(car_number)

        if call.message.photo:
            user_photo = call.message.photo[-1].file_id
            user_text = call.message.caption.split(":")[1][2:]

            for subscribed_user_id in subscribed_users:
                await bot.send_photo(
                    subscribed_user_id,
                    photo=user_photo,
                    caption=f'По номеру "{car_number}" новый комментарий! \nСам комментарий: {user_text}',
                )

            await call.message.delete()
            await call.message.answer("Комментарий одобрён ✅")
        else:
            user_text = call.message.text.split(":")[1][2:]
            user_photo = None

            for subscribed_user_id in subscribed_users:
                await bot.send_message(
                    subscribed_user_id,
                    f'По номеру "{car_number}" новый комментарий! \nСам комментарий: {user_text}',
                )

            await call.message.edit_text("Комментарий одобрён ✅")

        await bot.send_message(
            user_id, f"""Ваш комментарий по номеру "{car_number}" опубликован! ✅ 
Ваш счёт пополнен на 5 монет!""")
        
        if not db.owner_exists(car_number):
            await bot.send_message(
                user_id,
                f"\n\nХотите прикрепить своё имя к номеру машины (если вы владелец)?",
                reply_markup=Keyboards.become_owner(),
            )

        report_id = random.randint(1, 9999999999)
        car_owner_username = db.get_car_owner_username(car_number)
        db.add_car_report(report_id, car_number, user_text, user_id, user_photo, car_owner_username)
        db.change_balance(user_id, 5)

    elif call.data.startswith("report_reject"):
        user_id = call.data.split("__")[1]
        car_number = call.data.split("__")[2]

        await call.message.edit_text("Комментарий отклонён ❌")
        await bot.send_message(
            user_id, f'Ваш комментарий по номеру "{car_number}" отклонили! ❌'
        )

    elif call.data.startswith("see_car_report") and call.data != "see_car_report_button":
        car_number = call.data.split("__")[1]
        await call.message.edit_text(
            f"Оплатите {db.get_setting()[1]} рублей за просмотр", reply_markup=Keyboards.paying_for_report(car_number)
        )

    elif call.data.startswith("report_paying"):
        setting = db.get_setting()
        car_number = call.data.split("__")[1]
        car_owner_username = db.get_car_owner_username(car_number)

        if not db.get_balance(user_id) >= setting[1]:
            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='На вашем балансе недостаточно средств!',
                show_alert=True
            )
            return

        db.change_balance(user_id, setting[1])

        await call.message.edit_text("С твоего счёта успешно списались средства ✅")
        await call.message.answer(("" if not car_owner_username else f"Владельцем машины является пользователь @{car_owner_username}.") + "\nСуществующие комментарии: ")

        data = await state.get_data()
        car_number = data["car_number"]
        car_reports = db.get_car_number_reports(car_number)
        subscribed_users = db.get_car_subscribe_users(car_number)

        for index, report in enumerate(car_reports):
            index += 1

            if report[4]:
                await call.message.answer_photo(
                    photo=report[4], caption=f"{index} комментарий: \n{report[3]}"
                )
            else:
                await call.message.answer(f"{index} комментарий: \n{report[3]}")

            db.add_report_to_history(user_id, report[1])

        if str(user_id) not in subscribed_users:
            await call.message.answer(
                f"Подписаться на уведомления по номеру {car_number}?",
                reply_markup=Keyboards.subscribe_for_reports(),
            )

    elif call.data == "report_subscribe":
        data = await state.get_data()
        car_number = data["car_number"]

        db.subscribe_user_for_car_number(car_number, user_id)
        db.add_subscribe_number(user_id, car_number)

        await call.message.edit_text("Теперь ты подписан на уведомления ✅")

    elif call.data == "no_report_subscribe":
        await call.message.edit_text("Ты не подписался на уведомления.")

    elif call.data == "see_car_report_button":
        await call.message.edit_text("Введите запрос в формате «х111хх777» или «79991112233»")

        await User.UserState.see_car_report_button.set()

    elif call.data == "profile":
        username = call.from_user.username
        user_balance = db.get_balance(user_id)

        await call.message.edit_text(
            f"👤 Твой профиль: \nИмя: {username} \nID: {user_id} \nБаланс: {user_balance}",
            reply_markup=Keyboards.balance_button(),
        )

    elif call.data == "replenish_balance":
        await call.message.edit_text(
            "Введите сумму, на которую хотите пополнить баланс"
        )

        await User.UserState.replenish_balance.set()

    elif call.data == "check_payment":
        data = await state.get_data()

        balance_replenish_amount = data["balance_replenish_amount"]
        random_label = data["random_label"]

        pay_history = yoomoney_client.operation_history(
            label=f"{user_id}__{random_label}"
        )

        if pay_history.operations:
            if pay_history.operations[0].status == "success":

                user = db.get_info_user(user_id)
                setting = db.get_setting()

                if user[5]:
                    amount = int(balance_replenish_amount / 100 * setting[3])
                    db.change_balance(user[5], amount)

                    await bot.send_message(
                        chat_id=user[5],
                        text=f'Ваш реферал пополнил баланс! Ваша награда: {amount} (валюта)'
                    )

                db.change_balance(user_id, balance_replenish_amount)
                await call.message.edit_text("Твой баланс успешно пополнен!", reply_markup=Keyboards.menu())

                return

        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='Оплата не найдена!'
        )

    elif call.data == "user_subscriptions":
        get_subscribe_car_numbers = db.get_subscribe_car_numbers(user_id)

        await call.message.edit_text(
            f"Ваши подписки на уведомления: {', '.join(get_subscribe_car_numbers)}"
        )

    elif call.data == "become_owner":
        await call.message.edit_text(
            f"Оплатите {db.get_setting()[2]} рублей за то, чтобы стать владельцем",
            reply_markup=Keyboards.paying_for_become_owner(),
        )

    elif call.data == "no_become_owner":
        await call.message.edit_text("Ты отказался от этой функции ✅")

    elif call.data == "becoming_owner_paying":
        data = await state.get_data()
        user_car_number = data["car_number"]

        setting = db.get_setting()

        if not db.get_balance(user_id) >= setting[2]:
            await bot.answer_callback_query(
                callback_query_id=call.id,
                text='На вашем балансе недостаточно средств!',
                show_alert=True
            )
            return

        db.change_balance(user_id, setting[2])

        await call.message.edit_text(
            "Вы оплатили функционал! Вам придёт уведомление, когда модератор одобрит вашу заявку!"
        )
        await bot.send_message(
            Config.admin_id[0],
            f"@{username} прислал заявку на право стать владельцем машины под номером {user_car_number}!",
            reply_markup=Keyboards.approve_or_reject_becoming_owner(
                user_id, user_car_number
            ),
        )

    elif call.data.startswith("becoming_owner_approve"):
        user_id = call.data.split("__")[1]
        car_number = call.data.split("__")[2]

        un = await bot.get_chat(user_id)

        db.add_owner_username(car_number, un.username)
        await call.message.edit_text("Заявка одобрена ✅")
        await bot.send_message(
            user_id,
            f'Вашу заявку на владение номером "{car_number}" одобрили ✅ \nТеперь вы владелец этого номера!',
        )

    elif call.data.startswith("becoming_owner_reject"):
        user_id = call.data.split("__")[1]
        car_number = call.data.split("__")[2]

        await call.message.edit_text("Заявка отклонена ❌")
        await bot.send_message(
            user_id,
            f'Вашу заявку на владение номером "{car_number}" отклонили! ❌',
        )

    elif call.data == 'reports':

        await User.history.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text='История купленных комментариев:',
            message_id=call.message.message_id,
            reply_markup=Keyboards.history(user_id, 0)
        )

    elif call.data == 'refferals':

        bot_name = await bot.get_me()

        await bot.send_message(
            chat_id=user_id,
            text=f'Приглашайте пользователей и зарабатывайте до {db.get_setting()[3]}% с их покупок!\n\n'
                 f'У Вас {len(db.get_ref(user_id))} реферал(ов)\n\n'
                 f'Ваша ссылка для приглашения:\n'
                 f't.me/{bot_name.username}?start={user_id}'
        )

    elif call.data == 'rules':

        await bot.send_message(
            chat_id=user_id,
            text="""⚠️ ПРАВИЛА ПОЛЬЗОВАНИЯ:
➖➖➖➖➖➖➖➖➖➖➖➖➖
❗️Запрещается присылать боту рекламные посты/ссылки, сообщения нарушающие законодательство Российской Федерации, а также флудить в записях.
❗️ Оскорблять сотрудников Тех. поддержки.
❗️Мы - работаем только c номерами, зарегистрированными на территории РФ.
❗️Мы - не отвечаем за списанные средства в ходе неверного указания данных во время проверки и не несём ответственности за списанные средства с баланса пользователя.
❗️Мы - не отвечаем за указанные данные, а так же записи оставленные пользователями.
❗️За нарушение одного из вышеуказанных требований - учётная запись может быть заблокирована без уведомления а также без возврата средств.

💊 Администрация имеет полное право - вносить изменения в данный раздел по своему усмотрению и без уведомлений остальных участников проекта."""
        )


async def user_history(call: types.CallbackQuery):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'next':
        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=Keyboards.history(user_id, int(temp[2]))
        )

    elif temp[1] == 'back':
        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=call.message.message_id,
            reply_markup=Keyboards.history(user_id, int(temp[2]))
        )

    elif temp[1] == 'menu':
        await User.menu.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text="""ДОБРО ПОЖАЛОВАТЬ🎈
➖➖➖➖➖➖➖➖➖➖➖➖➖
Бот покажет что пишут о вас другие люди!
Посмотрите, может о вас уже написали👨‍💻 
Поиск осуществляется по «Госномеру», «Номеру телефона» или «VIN-коду». 
➖➖➖➖➖➖➖➖➖➖➖➖➖
Выберите нужное действие:""",
            message_id=call.message.message_id,
            reply_markup=Keyboards.menu()
        )
    elif temp[1] == 'close':
        await bot.delete_message(call.from_user.id, call.message.message_id)

    else:
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        report = db.get_report_info(temp[1])
        bot_name = await bot.get_me()
        car_number = temp[2]

        if report[4]:
            await bot.send_photo(
                chat_id=user_id,
                photo=report[4],
                caption=report[3] + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}",
                reply_markup=Keyboards.close()
            )
        else:
            await bot.send_message(
                chat_id=user_id,
                text=report[3] + f"\nСсылка на данный номер: t.me/{bot_name.username}?start=c_{car_number}_{user_id}",
                reply_markup=Keyboards.close()
            )


def hand_add(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state="*")

    dp.register_message_handler(
        add_car_report_button, state=User.UserState.add_car_report_button
    )

    dp.register_message_handler(
        see_car_report_button, state=User.UserState.see_car_report_button
    )

    dp.register_message_handler(replenish_balance, state=User.UserState.replenish_balance)

    dp.register_message_handler(
        add_own_car_report,
        state=User.UserState.add_own_car_report,
        content_types=types.ContentType.ANY,
    )

    dp.register_callback_query_handler(callback_query_handler, state=User.menu.start)

    dp.register_callback_query_handler(user_history, lambda c: c.data and c.data.startswith('us'),
                                       state=User.history.start)
