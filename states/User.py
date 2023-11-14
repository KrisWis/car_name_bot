from aiogram.dispatcher.filters.state import State, StatesGroup


class menu(StatesGroup):
    start = State()


class history(StatesGroup):
    start = State()


class admin(StatesGroup):
    start = State()
    mail = State()
    ban = State()
    update_setting = State()


class UserState(StatesGroup):
    add_car_report_button = State()
    add_own_car_report = State()
    see_car_report_button = State()
    replenish_balance = State()