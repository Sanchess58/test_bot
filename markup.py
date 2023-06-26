from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.callback_data import CallbackData

"""Main Menu"""
btnform = KeyboardButton("Оставить заявку")
btnbuy = KeyboardButton("Купить товар")
btnbalance = KeyboardButton("Мой баланс")
markup = ReplyKeyboardMarkup(
    resize_keyboard=True
    ).add(
        btnform,
        btnbuy,
        btnbalance)

"""Admin Button"""
btnsendmessage = KeyboardButton("Отправить сообщение пользователям")
markup_admin = ReplyKeyboardMarkup(
    resize_keyboard=True
    ).add(
        btnform,
        btnbuy,
        btnbalance,
        btnsendmessage)


"""Inline Buttons"""
cb_form = CallbackData('form', 'form_text')
form = InlineKeyboardMarkup(row_width=1)
btnsale = InlineKeyboardButton(
    text="Продажа",
    callback_data=cb_form.new("Продажа")
)
btnproduction = InlineKeyboardButton(
    text="Производство",
    callback_data=cb_form.new("Производство")
)
btnservices = InlineKeyboardButton(
    text="Оказание услуг",
    callback_data=cb_form.new("Оказание услуг")
)

form.insert(btnsale)
form.insert(btnproduction)
form.insert(btnservices)


"""Platforms Buttons"""
cb_platform = CallbackData('platform', 'platform_text')
platform_form = InlineKeyboardMarkup(row_width=1)
btntelegram = InlineKeyboardButton(
    text="Телеграм",
    callback_data=cb_platform.new("Телеграмм")
)
btnwhatsapp = InlineKeyboardButton(
    text="Ватcапп",
    callback_data=cb_platform.new("Ватсапп")
)
btnviber = InlineKeyboardButton(
    text="Вайбер",
    callback_data=cb_platform.new("Вайбер")
)

platform_form.insert(btntelegram)
platform_form.insert(btnwhatsapp)
platform_form.insert(btnviber)


"""Products Button"""
cb_products = CallbackData('products', 'products_text')
products_form = InlineKeyboardMarkup(row_width=1)
btnproduct1 = InlineKeyboardButton(
    text="Купить 1 раз",
    callback_data=cb_products.new("Купить 1 раз")
)
btnproduct2 = InlineKeyboardButton(
    text="Купить 2 раза",
    callback_data=cb_products.new("Купить 2 раза")
)

products_form.insert(btnproduct1)
products_form.insert(btnproduct2)
