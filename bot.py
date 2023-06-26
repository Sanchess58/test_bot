from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType
from aiogram.utils.exceptions import ChatNotFound
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import markup
from config import ADMIN, BOT_TOKEN, YOOTOKEN
from db import applications, connect, exc, users
from validate import check_number


async def reminder(from_id: int):
    try:
        global TIMER
        if TIMER:
            await bot.send_message(from_id, "Ты забыл заполнить анкету!")
    except ChatNotFound:
        print("Данного пользователя нет в базе")

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)
apschedule = AsyncIOScheduler(timezone="Europe/Moscow")
TIMER = False


# создаём форму и указываем поля
class Form(StatesGroup):
    business_direction = State()
    platform_develop = State()
    budget_start = State()
    budget_finish = State()
    number = State()


class SendAll(StatesGroup):
    text_message = State()


@dp.message_handler(commands=['start'])
async def get_message(message: types.Message):
    user = users.insert().values(telegram_id=message.from_id)
    connect.execute(user)
    if message.from_user.id == ADMIN:
        await bot.send_message(
                message.from_user.id,
                "Здравствуй, админ, вас привествует бот!",
                reply_markup=markup.markup_admin
        )
    else:
        await bot.send_message(
            message.from_user.id,
            "Здравствуйте, вас привествует бот!",
            reply_markup=markup.markup
        )


@dp.message_handler(text='Отправить сообщение пользователям')
async def pre_sendall(message: types.Message):
    """Функция отвечающая за текст"""
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.send_message(
        message.from_user.id,
        "Напишите сообщение рассылки"
    )
    await SendAll.text_message.set()


@dp.message_handler(state=SendAll.text_message)
async def sendall(message: types.Message, state: FSMContext):
    """Функция отвечающая за рассылку"""
    async with state.proxy() as data:
        data['text'] = message.text
    await state.finish()
    get_users = users.select()
    res = connect.execute(get_users)
    for user_id in res:
        if user_id[1] != ADMIN:
            await bot.send_message(user_id[1], data._data.get('text'))


@dp.message_handler(text='Оставить заявку')
async def submit_your_application(message: types.Message):
    """Функция отвечающая за получение направления бизнеса."""
    global TIMER
    TIMER = True
    apschedule.add_job(
        reminder,
        "date",
        run_date=datetime.now()+timedelta(minutes=10),
        kwargs={'from_id': message.from_user.id}
    )
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.send_message(
        message.from_user.id,
        "Какое направление вашего бизнеса?",
        reply_markup=markup.form
    )
    await Form.business_direction.set()


@dp.callback_query_handler(
        markup.cb_form.filter(),
        state=Form.business_direction
    )
async def business_direction(
    call: types.CallbackQuery,
    callback_data: dict, state: FSMContext
):
    """Функция отвечающая за
    получение платформы для которой будет разрабатываться бот."""
    async with state.proxy() as data:
        data['business_direction'] = callback_data.get("form_text")
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(
        call.from_user.id,
        "На какой платформе вы хотите разработать чат-бот?",
        reply_markup=markup.platform_form
    )
    await Form.next()


@dp.callback_query_handler(
        markup.cb_platform.filter(),
        state=Form.platform_develop
    )
async def start_budget(
    call: types.CallbackQuery,
    callback_data: dict, state: FSMContext
):
    """Функция отвечающая за получение бюджета пользователя."""
    async with state.proxy() as data:
        data['platform_develop'] = callback_data.get("platform_text")
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(
        call.from_user.id,
        "Какой у вас бюджет? \n Введите значение от"
    )
    await Form.next()


@dp.message_handler(state=Form.budget_start)
async def finish_budget(message: types.Message, state: FSMContext):
    """Функция отвечающая за получение бюджета пользователя."""
    async with state.proxy() as data:
        data['budget_start'] = int(message.text)
    await bot.send_message(message.from_user.id, "Введите значение до")
    await Form.next()


@dp.message_handler(state=Form.budget_finish)
async def platform_f(message: types.Message, state: FSMContext):
    """Функция отвечающая за получение бюджета пользователя."""
    async with state.proxy() as data:
        if data['budget_start'] < int(message.text):
            data['budget_finish'] = int(message.text)
            await bot.send_message(
                message.from_user.id,
                "Спасибо за ответы на вопросы, осталось ввести номер телефона"
            )
            await Form.next()
        else:
            await bot.send_message(
                message.from_user.id,
                f"Число должно быть больше {data['budget_start']}"
            )


@dp.message_handler(state=Form.number)
async def get_number(message: types.Message, state: FSMContext):
    """Функция отвечающая за получение бюджета пользователя."""
    global TIMER
    try:
        if check_number(message.text) and message.text != "":
            async with state.proxy() as data:
                data['number'] = int(message.text)
                appl = applications.insert().values(
                    business=data._data.get("business_direction"),
                    platform=data._data.get("platform_develop"),
                    budget_start=data._data.get("budget_start"),
                    budget_finish=data._data.get("budget_finish"),
                    number=data._data.get("number")
                    )
                connect.execute(appl)
            await bot.send_message(
                message.from_user.id,
                "Анкета успешно заполнена!"
            )
            await state.finish()
            TIMER = False
            my_balance = applications.select().where(
                applications.c.number == int(message.text)
            )
            result = connect.execute(my_balance)
            result = result.fetchone()
            await bot.send_message(
                ADMIN,
                f"Заявка от пользователя с номером -> {result[5]}\n"
                f"Направление бизнеса: {result[1]}\n"
                f"Бот нужен для платформы -> {result[2]} \n"
                f"Бюджет от {result[3]} до {result[4]}"
            )
        else:
            await bot.send_message(
                message.from_user.id,
                "Введите корректный номер телефона"
            )
    except exc.IntegrityError:
        await bot.send_message(
                message.from_user.id,
                "Такой номер уже зарегистрирован!"
            )


@dp.message_handler(text='Купить товар')
async def buy_product(message: types.Message):
    """Функция показывающая товары в наличии."""
    await bot.delete_message(message.from_user.id, message.message_id)
    await bot.send_message(
        message.from_user.id,
        "Товары в наличии",
        reply_markup=markup.products_form
    )


@dp.callback_query_handler(markup.cb_products.filter())
async def get_products(call: types.CallbackQuery, callback_data: dict):
    """"Функция выдающая пользователю страницу с оплатой."""
    amount = 20000 if callback_data.get("products_text") == "Купить 1 раз" else 40000
    price = [{"label": "Руб", "amount": amount}]
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=callback_data.get("products_text"),
        description=f"Товар '{callback_data.get('products_text')}'",
        payload="prod",
        provider_token=YOOTOKEN,
        currency="RUB",
        start_parameter="test_bot",
        prices=price
    )


@dp.pre_checkout_query_handler()
async def proccess_get_product(pre_get_product: types.PreCheckoutQuery):
    """Подтверждение наличия товара"""
    await bot.answer_pre_checkout_query(pre_get_product.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def success_payload(message: types.Message):
    """Функция успешной покупки!"""
    money = message.successful_payment.total_amount // 100
    if message.successful_payment.invoice_payload == "prod":
        await bot.send_message(message.from_user.id, "Спасибо за покупку!")
        user = users.update().where(
            users.c.telegram_id == message.from_id
            ).values({users.c.balance: users.c.balance+money})
        connect.execute(user)


@dp.message_handler(text='Мой баланс')
async def m_balance(message: types.Message):
    """Функция показывающая баланс пользователя."""
    await bot.delete_message(message.from_user.id, message.message_id)
    my_balance = users.select().where(users.c.telegram_id == message.from_id)
    result = connect.execute(my_balance)
    await bot.send_message(
        message.from_user.id,
        f"У вас на балансе {result.fetchone()[2]} условных единиц"
    )


if __name__ == "__main__":
    apschedule.start()
    executor.start_polling(dp, skip_updates=True)
