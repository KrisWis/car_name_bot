import asyncio
import aiogram
from InstanceBot import bot
from aiogram import types, Dispatcher
from keyboards import Keyboards
from aiogram.dispatcher import FSMContext
from database import db
from states import User
import Config


async def admin(message: types.Message):
    user_id = message.from_user.id

    if user_id in Config.admin_id:

        await User.admin.start.set()
        await bot.send_message(
            chat_id=user_id,
            text='Админ меню',
            reply_markup=Keyboards.admin()
        )


async def choice(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'mail':
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        await User.admin.mail.set()
        await bot.send_message(
            chat_id=user_id,
            text='Отправьте текст для рассылки, разметка HTML.'
        )
    elif temp[1] == 'ban':
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        await User.admin.ban.set()
        await bot.send_message(
            chat_id=user_id,
            text='Отправьте ID пользователя для блокировки.'
        )

    elif temp[1] == 'close':
        await bot.delete_message(user_id, call.message.message_id)

    else:
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅'
        )

        async with state.proxy() as data:
            data['row'] = temp[1]

        await User.admin.update_setting.set()
        await bot.send_message(
            chat_id=user_id,
            text='Введите новое значение цифрой!'
        )


async def mail_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    try:
        r = await bot.send_message(
            chat_id=user_id,
            text=message.text
        )
        await bot.delete_message(user_id, r.message_id)
    except aiogram.exceptions.CantParseEntities:
        await message.answer('Неверное заполнение HTML кода.')
        return

    async with state.proxy() as data:
        data['mail_text'] = message.text

    await bot.send_message(
        chat_id=user_id,
        text=f'Текст рассылки:\n\n'
             f'{message.text}\n\n'
             f'Запустить рассылку?',
        reply_markup=Keyboards.admin_mail()
    )


async def mail_accept(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    temp = call.data.split('|')

    if temp[1] == 'yes':
        async with state.proxy() as data:
            text = data['mail_text']

        count = 0
        reject = 0
        for i in db.get_users():

            await bot.edit_message_text(
                chat_id=user_id,
                text=f'Рассылка запущена.\n\n'
                     f'Отправлено: {count}\n'
                     f'Ошибок: {reject}',
                message_id=call.message.message_id
            )

            try:
                await bot.send_message(
                    chat_id=i[0],
                    text=text
                )
                count += 1
            except aiogram.exceptions.BotBlocked:
                reject += 1
            except Exception as e:
                print(e)
                reject += 1

            await asyncio.sleep(0.1)

        await User.admin.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text=f'Рассылка запущена.\n\n'
                 f'Отправлено: {count}\n'
                 f'Ошибок: {reject}',
            message_id=call.message.message_id,
            reply_markup=Keyboards.admin()
        )

    if temp[1] == 'no':
        await bot.answer_callback_query(
            callback_query_id=call.id,
            text='✅ Отменено'
        )

        await User.admin.start.set()
        await bot.edit_message_text(
            chat_id=user_id,
            text='Админ меню',
            reply_markup=Keyboards.admin()
        )


async def update_setting(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if not message.text.isdigit():
        await message.answer('Отправьте значение числом!')
        return

    async with state.proxy() as data:
        row = data['row']

    db.update_setting(row, message.text)

    await User.admin.start.set()
    await bot.send_message(
        chat_id=user_id,
        text='Значение успешно изменено!',
        reply_markup=Keyboards.admin()
    )


async def user_ban(message: types.Message):
    user_id = message.from_user.id

    if not message.text.isdigit():
        await message.answer('ID - это числовое значение.')
        return

    db.ban_user(user_id, 1)

    await User.admin.start.set()
    await bot.send_message(
        chat_id=user_id,
        text='Пользователь заблокирован!',
        reply_markup=Keyboards.admin()
    )


def hand_add(dp: Dispatcher):
    dp.register_message_handler(admin, commands=['admin'], state='*')
    dp.register_callback_query_handler(choice, lambda c: c.data and c.data.startswith('a'), state=User.admin.start)
    dp.register_message_handler(update_setting, content_types=['text'], state=User.admin.update_setting)
    dp.register_message_handler(mail_text, content_types=['text'], state=User.admin.mail)
    dp.register_callback_query_handler(mail_accept, lambda c: c.data and c.data.startswith('m'), state=User.admin.mail)
    dp.register_message_handler(user_ban, content_types=['text'], state=User.admin.ban)
