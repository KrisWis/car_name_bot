import math

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from database import db


def menu():
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(
        *[
            InlineKeyboardButton(
                text="Добавить комментарий📝", callback_data="add_car_report_button"
            ),
            InlineKeyboardButton(
                text="Посмотреть комментарии📄", callback_data="see_car_report_button"
            ),
            InlineKeyboardButton(text="Профиль 👤", callback_data="profile"),
            InlineKeyboardButton(text="Комментарии 🧾", callback_data="reports"),
            InlineKeyboardButton(text="Реф. система 👥", callback_data="refferals"),
            InlineKeyboardButton(text="Правила 📖", callback_data="rules"),
        ]
    )

    return kb


def add_own_car_report():
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton(text="Добавить 🖌", callback_data="add_own_car_report"))

    return kb


def add_or_see_report(car_number):
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(text="Добавить 🖌", callback_data="add_own_car_report"),
            InlineKeyboardButton(text="Посмотреть 📝", callback_data=f"see_car_report__{car_number}"),
        ]
    )

    return kb


def see_report(car_number):
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton(text="Посмотреть 📝", callback_data=f"see_car_report__{car_number}"))

    return kb


def approve_or_reject_report(user_id, car_number):
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(
                text="Одобрить ✅",
                callback_data=f"report_approve__{user_id}__{car_number}",
            ),
            InlineKeyboardButton(
                text="Отклонить ❌",
                callback_data=f"report_reject__{user_id}__{car_number}",
            ),
        ]
    )

    return kb


def paying_for_report(car_number):
    kb = InlineKeyboardMarkup()

    kb.add(InlineKeyboardButton(text="Оплатить 💳", callback_data=f"report_paying__{car_number}"))

    return kb


def subscribe_for_reports():
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(text="Да ✅", callback_data=f"report_subscribe"),
            InlineKeyboardButton(text="Нет ❌", callback_data=f"no_report_subscribe"),
        ]
    )

    return kb


def balance_button():
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(
                text="Пополнить баланс", callback_data="replenish_balance"
            ),
            InlineKeyboardButton(
                text="Ваши подписки", callback_data="user_subscriptions"
            ),
        ]
    )

    return kb


def check_payment():
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(text="Проверить оплату ", callback_data="check_payment")
    )

    return kb


def become_owner():
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(text="Да ✅", callback_data=f"become_owner"),
            InlineKeyboardButton(text="Нет ❌", callback_data=f"no_become_owner"),
        ]
    )

    return kb


def paying_for_become_owner():
    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(text="Оплатить 💳", callback_data="becoming_owner_paying")
    )

    return kb


def approve_or_reject_becoming_owner(user_id, car_number):
    kb = InlineKeyboardMarkup()

    kb.add(
        *[
            InlineKeyboardButton(
                text="Одобрить ✅",
                callback_data=f"becoming_owner_approve__{user_id}__{car_number}",
            ),
            InlineKeyboardButton(
                text="Отклонить ❌",
                callback_data=f"becoming_owner_reject__{user_id}__{car_number}",
            ),
        ]
    )

    return kb


def history(user_id, remover):
    kb = InlineKeyboardMarkup(row_width=3)

    user_history = db.get_info_user(user_id)[3]

    for i, a in enumerate(range(remover, len(user_history))):
        if i < 10:
            report = db.get_report_info(user_history[a])
            kb.add(InlineKeyboardButton(text=f'ID: {report[1]} / {report[2]}', callback_data=f'us|{report[1]}|{report[2]}'))

    if len(user_history) <= 10:
        pass

    elif len(user_history) > 10 > remover:
        kb.add(InlineKeyboardButton(text='➡️', callback_data=f'us|next|{remover + 10}'))

    elif remover + 10 >= len(user_history):
        kb.add(InlineKeyboardButton(text='⬅️', callback_data=f'us|back|{remover - 10}'))

    else:
        kb.add(InlineKeyboardButton(text='⬅️', callback_data=f'us|back|{remover - 10}'),
               InlineKeyboardButton(text=f'{str(remover + 10)[:-1]}/{math.ceil(len(user_history) / 10)}',
                                    callback_data='...'),
               InlineKeyboardButton(text='➡️', callback_data=f'us|next|{remover + 10}'))

    kb.add(InlineKeyboardButton(text='Вернуться назад', callback_data='us|menu'))
    return kb


def close():
    kb = InlineKeyboardMarkup(row_width=1)

    kb.add(InlineKeyboardButton(text='Закрыть', callback_data='us|close'))

    return kb


def admin():
    kb = InlineKeyboardMarkup(row_width=2)

    setting = db.get_setting()

    kb.add(InlineKeyboardButton(text=f'Рассылка', callback_data='a|mail'))
    kb.add(InlineKeyboardButton(text=f'Стоимость отчета ({setting[1]}Р)', callback_data='a|report_amount'))
    kb.add(InlineKeyboardButton(text=f'Стоимость владельца ({setting[2]}Р)', callback_data='a|owner_amount'))
    kb.add(InlineKeyboardButton(text=f'Награда реферала ({setting[3]}%)', callback_data='a|ref_percent'))
    kb.add(InlineKeyboardButton(text='Заблокировать пользователя', callback_data='a|ban'))
    kb.add(InlineKeyboardButton(text='Закрыть', callback_data='a|close'))

    return kb


def admin_mail():
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(InlineKeyboardButton(text='Запустить', callback_data='m|yes'),
           InlineKeyboardButton(text='Отменить', callback_data='m|no'))

    return kb
