import datetime
import random
import string
from aiogram.filters import  Command, or_f
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select
from datetime import datetime
from aiogram import types
from aiogram.filters import or_f, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.orm import joinedload
from dateutil import parser
from collections import defaultdict

from sqlalchemy import create_engine, select, select, delete
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
import time
from aiogram import F, types, Router, Bot
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from geopy.distance import geodesic
from flask import Flask, request
from telegram import Update
from telegram.error import TelegramError
from aiogram.filters import StateFilter
import re
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import random
import string
from aiogram import Bot, F
from aiogram.types import (
    CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice,
    Message, PreCheckoutQuery, SuccessfulPayment
)
from decimal import Decimal
from aiogram import Router, F
from aiogram.types import CallbackQuery, PreCheckoutQuery, LabeledPrice, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from sqlalchemy.ext.asyncio import AsyncSession
import datetime
import random
import string
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from filters.chat_types import ChatTypeFilter
from kbds import reply
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from kbds.inline import get_callback_btns
from sqlalchemy.ext.asyncio import AsyncSession
from filters.chat_types import ChatTypeFilter
from kbds import reply
from database.orm_query import (
    orm_get_makers_by_category,
    orm_get_products_by_maker,
    orm_get_product,
    orm_add_user,
    get_user_spent,
    get_user_status,
    get_all_user_ids,
    count_referrals,
    get_products_with_tastes,
    update_product_quantity,
    update_user_spent,
    delete_promo_code,
    orm_get_makers_by_category,
    get_products_with_tastes,
    get_user_balance,
    update_product_quantity,
    get_user_favourites

 
)
from aiogram.types import CallbackQuery
from database.models import  Product, Promocode, Order, User, Favourite, Category, CartItem
user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(["private"]))
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

sub_router = Router()
sub_router.message.filter(ChatTypeFilter(["private"]))
CHANNEL_ID = "-1002457676283"
ROLES = [ "Прохожий ❤️","Покупатель 💸","Постоянник ❤️","Амбассадор Смоки Вилда 😍", ]
TOKEN = "8045332204:AAEjbQnp3BMfSpbKGIYV9CH4e-2-xJOZMPU"
bot = Bot(token=TOKEN)
# dp = Dispatcher()
COMMISSION_RATE = Decimal('0.03')
OFFICE_COORDS = (53.535315, 49.349094)
USER_ID =  -1002292552917
#USER_ID = 6777500292

latitude = 53.535315 # Широта
longitude = 49.349094  # Долгота




BOT_NICKNAME = "SmokyWild"
@user_private_router.message(Command('start'))
async def start_cmd(message: types.Message, session: AsyncSession):
    user = message.from_user
    user_id = user.id
    user_ids = await get_all_user_ids(session)

    if user_id not in user_ids:
        start_command = message.text
        referrer_id = None
        if start_command.startswith("/start "):
            referrer_id = start_command.split(" ")[1]
            if referrer_id.isdigit():
                referrer_id = int(referrer_id)
                if referrer_id != user_id:
                    spent = await get_user_spent(session, user_id)
                    status = await get_user_status(session, user_id)
                    if user.username is None:
                        username = "@" + (user.first_name or "username")
                    else:
                        username = user.username
                    await orm_add_user(
                        session,
                        user_id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        phone=None,
                        username=username,
                        status=status,
                        referrer_id=referrer_id,
                        balance=0
                    )
                    try:
                        await bot.send_message(referrer_id, "По вашей ссылке зарегистрировался новый пользователь!")
                    except Exception as e:
                        print(f"Failed to send message to referrer: {e}")
                else:
                    await message.answer("Нельзя регистрироваться по собственной реферальной ссылке!")
            else:
                await message.answer("Неверный формат реферальной ссылки!")
        else:
            spent = await get_user_spent(session, user_id)
            status = await get_user_status(session, user_id)
            if user.username is None:
                username = "@" + (user.first_name or "username")
            else:
                username = user.username
            is_subscribed = await check_subscription(user.id)
            if is_subscribed:
                await orm_add_user(
                    session,
                    user_id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=None,
                    username=username,
                    status=status,
                    referrer_id=referrer_id,
                    balance=0
                )

    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        await message.answer("👋 Привет! Добро пожаловать в наш магазин!\nЕсли ты ищешь качественные устройства, жидкости и аксессуары для вейпинга, то ты попал по адресу.\n\n❤️ У нас ты найдешь широкий ассортимент продукции, в наличии или под заказ.\n\n📍 Доставляем по всему Тольятти! От суммы чека 1000р. Новик доставка бесплатная\n\nАккаунт тех. поддержки - @SmokyWild | Время работы 10:00-22:00",
                              reply_markup=reply.start_kb2.as_markup(
                                  resize_keyboard=True,
                                  input_field_placeholder='Что Вас интересует?'))

    else:
        await message.answer("Подпишитесь на канал!", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                [InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
            ]
        ))


async def check_subscription(user_id):
    return True
    # try:
    #     member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    #     return member.status in ['member', 'creator', 'administrator']
    # except Exception as e:
    #     logging.error(f"Error checking subscription: {e}")
    #     return False

@user_private_router.message(Command('support'))
async def support_cmd(message: types.Message, session: AsyncSession):
    await message.answer("хае")


@user_private_router.callback_query(F.data.startswith("activate_start"))
async def process_callback_start(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_subscribed = await check_subscription(user_id)

    if is_subscribed:
        await callback.message.answer("👋 Привет! Добро пожаловать в наш магазин!\nЕсли ты ищешь качественные устройства, жидкости и аксессуары для вейпинга, то ты попал по адресу.\n\n❤️ У нас ты найдешь широкий ассортимент продукции, в наличии или под заказ.\n\n📍 Доставляем по всему Тольятти! От суммы чека 1000р. Новик доставка бесплатная\n\nАккаунт тех. поддержки - @SmokyScreenShop | Время работы 10:00-22:00",
                                      reply_markup=reply.start_kb2.as_markup(
                                          resize_keyboard=True,
                                          input_field_placeholder='Что Вас интересует?'))
    else:
        await callback.message.answer("Подпишитесь на канал!", reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                [types.InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
            ]
        ))


@user_private_router.message(or_f(Command("profile"), (F.text.lower() == "профиль 🙋‍♂️"), ))
async def profile_cmd(message: types.Message, session: AsyncSession):
    user = message.from_user
    user_id = user.id
    spent = await get_user_spent(session, user_id)
    status = await get_user_status(session, user_id)

    if user.username is None:
        username = "@" + (user.first_name or "username")
    else:
        username = "@" + user.username

    is_subscribed = await check_subscription(user.id)
    if is_subscribed:
        await orm_add_user(
            session,
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=None,
            username=username,
            status=status,
            referrer_id=None,
            balance=0
        )

        bal = await get_user_balance(session, user_id)
        await message.answer(
            f"👨 Ваш профиль\nЛогин: <b>{username}</b>\nСтатус: <b>{status}</b>\n\n💰 Покупок на сумму: <b>{spent:.2f}₽</b>\n🌫️ Дымки: <b>{bal}</b>",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Мои заказы", callback_data="show_user_orders")],
                ]
            )
        )
    else:
        await message.answer(
            "Подпишитесь на канал!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                    [InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
                ]
            )
        )

@user_private_router.callback_query(lambda c: c.data == "show_user_orders")
async def show_user_orders(callback_query: types.CallbackQuery, session: AsyncSession):
    user_id = callback_query.from_user.id
    stmt = (
        select(Order)
        .options(joinedload(Order.product))
        .where(Order.user_id == user_id)
        .order_by(Order.id.desc())
    )
    result = await session.execute(stmt)
    orders = result.scalars().unique().all()

    if not orders:
        await callback_query.message.answer("У вас нет активных заказов.")
        return

    order_groups = defaultdict(list)
    for order in orders:
        order_groups[order.order_number].append(order)

    keyboard = []
    for order_number, order_group in order_groups.items():
        order_number_last_four = order_number[-4:]
        keyboard.append([InlineKeyboardButton(text=f"Заказ {order_number_last_four}", callback_data=f"order_{order_group[0].id}")])

    await callback_query.message.answer("Ваши заказы:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback_query.answer()

@user_private_router.callback_query(lambda c: c.data.startswith("order_"))
async def show_order_details(callback_query: types.CallbackQuery, session: AsyncSession):
    order_id = int(callback_query.data.split("_")[1])
    user_id = callback_query.from_user.id
    
    # Получаем заказ по order_id
    stmt = (
        select(Order)
        .options(joinedload(Order.product))
        .where(Order.id == order_id, Order.user_id == user_id)
    )
    result = await session.execute(stmt)
    order = result.scalars().unique().one_or_none()

    if not order:
        await callback_query.answer("Заказ не найден.")
        return

    # Получаем все заказы с тем же order_number
    stmt = (
        select(Order)
        .options(joinedload(Order.product))
        .where(Order.order_number == order.order_number, Order.user_id == user_id)
    )
    result = await session.execute(stmt)
    orders = result.scalars().unique().all()

    if not orders:
        await callback_query.answer("Заказ не найден.")
        return

    order_message = f"Заказ: <strong>{order.order_number}</strong>\n\n"
    total_price = 0

    for order in orders:
        product = order.product
        created_time = parser.isoparse(str(order.created)).strftime('%Y-%m-%d %H:%M:%S')
        order_message += (
            f"Название: <strong>{product.name}</strong>,\nПроизводитель: <strong>{product.maker}</strong>,\nВкус: <strong>{product.taste}</strong>\n"
            f"Цена: <strong>{order.price}</strong>\n"
            f"Количество: <strong>{order.quantity}</strong>\n"
            f"Состояние оплаты: <strong>{order.payment_status}</strong>\n"
            f"Статус: <strong>{order.order_status}</strong>\n"
            f"Время создания: <strong>{created_time}</strong>\n\n"
        )
        total_price += order.price * order.quantity

    order_message += f"Общая цена: <strong>{total_price}</strong>\n"

    await callback_query.message.edit_text(order_message)
    await callback_query.answer()

@user_private_router.message(or_f(Command("order"), (F.text.lower() == "Мои заказы 📋")))
async def order_cmd(message: types.Message, session: AsyncSession):
    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        await show_user_orders(message, session)
    else:
        await message.answer("Подпишитесь на канал!", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                [InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
            ]
        ))

# @user_private_router.callback_query(F.data.startswith("order_"))
# async def order_details_callback(callback_query: types.CallbackQuery, session: AsyncSession):
#     order_id = int(callback_query.data.split("_")[1])
#     await show_order_details(callback_query, session, order_id)



def get_callback_btns2(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(types.InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


@user_private_router.message(or_f(Command("loyalty_system"), (F.text.lower() == "система лояльности 📢")))
async def loyalty_system_cmd(message: types.Message, session: AsyncSession):
    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        telegram_user_id = message.from_user.id

        stmt = select(User).where(User.user_id == telegram_user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if user is None:
            await message.answer("Пользователь не найден в базе данных.")
            return

        user_id = user.user_id

        try:
            bal = await get_user_balance(session, user_id)
        except ValueError as e:
            await message.answer(str(e))
            return

        ref = await count_referrals(session, user_id)

        stmt = select(Promocode).where(Promocode.user_id == user.id)
        result = await session.execute(stmt)
        promocodes = result.scalars().all()

        btns = {}
        if promocodes:
            for promocode in promocodes:
                if promocode.discount_type == "PERCENT":
                    zna = "%"
                else:
                    zna = "₽"
                number = int(promocode.discount_amount)
                button_text = f"Промокод на {number} {zna}"
                btns[button_text] = f"promo_{promocode.name}"
        else:
            btns["Нет доступных промокодов"] = "no_promo"

        keyboard = get_callback_btns2(btns=btns)

        await message.answer(
            f"🤝 Реферальная программа\nЕсли человек перейдёт по вашей реферальной ссылке, то станет вашим рефералом.\nС каждой его покупки вы будете получать процент на свой баланс дымков!\n🌫 Ваши дымки:  {bal}\n✉️ Кол-во рефералов: {ref}\n\n🛎 Ссылка\n<code>https://t.me/{BOT_NICKNAME}?start={telegram_user_id}</code>",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "Подпишитесь на канал!",
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [types.InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                    [types.InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
                ]
            )
        )


@user_private_router.callback_query(lambda c: c.data.startswith('promo_'))
async def process_callback_promo(callback_query: types.CallbackQuery):
    promocode_name = callback_query.data.split('_')[1]
    await callback_query.message.answer(f"Ваш промокод: <code>{promocode_name}</code>", parse_mode="HTML")
    await callback_query.answer()


class FavouritesState(StatesGroup):
    choosing_taste = State()


def get_favourites_keyboard(btns: dict):
    builder = InlineKeyboardBuilder()
    for text, callback_data in btns.items():
        builder.button(text=text, callback_data=callback_data)
    return builder.as_markup()


@user_private_router.message(or_f(Command("favourites"), (F.text.lower() == "избранное ❤️")))
async def favourites_cmd(message: types.Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id

    stmt = select(Favourite).filter(Favourite.user_id == user_id).options(selectinload(Favourite.product))
    result = await session.execute(stmt)
    favourites = result.scalars().all()

    if not favourites:
        await message.answer("У вас пока нет избранных товаров.")
        return

    tastes = set(favourite.product.taste for favourite in favourites)
    btns = {taste: f"taste_{taste}" for taste in tastes}

    await state.set_state(FavouritesState.choosing_taste)
    await message.answer(
        text="❤️  Ваши избранные товары:",
        reply_markup=get_favourites_keyboard(btns=btns)
    )


@user_private_router.callback_query(F.data.startswith("taste_"), FavouritesState.choosing_taste)
async def taste_selected(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    taste = callback.data.split("_")[1]
    user_id = callback.from_user.id

    stmt = select(Favourite).join(Product).filter(
        Favourite.user_id == user_id,
        Product.taste == taste
    ).options(selectinload(Favourite.product))
    result = await session.execute(stmt)
    favourite = result.scalar()

    if not favourite:
        await callback.message.answer("Товар с таким вкусом не найден в избранном.")
        return

    product = favourite.product
    product_id = product.id

    keyboard = [
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(1, 6)
        ],
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(6, 11)
        ],
        [
            InlineKeyboardButton(text="Более 10 шт.", callback_data="opt_")
        ],
        [
            InlineKeyboardButton(text="Удалить", callback_data=f"d_fav_{product.id}"),
            InlineKeyboardButton(text="Главная", callback_data="activate_start")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    stmt = select(Product.quantity).filter(Product.id == product_id)
    result = await session.execute(stmt)
    quantity_on_stock = result.scalar()
    if quantity_on_stock is None:
        await callback.message.answer("Товар не найден на складе.")
        await callback.answer()
        return
    if quantity_on_stock < 0:
        try:
            await bot.send_message(USER_ID, f"Warning: Product '{product.name}' has a quantity less than 0!")
        except Exception as e:
            logging.error(f"Failed to send message to admin: {e}")
    if quantity_on_stock < 1:
        nali = "Только под заказ"
    elif 0 < quantity_on_stock < 11:
        nali = f"Количество товара: {quantity_on_stock}"
    else:
        nali = "Товар есть в наличие"
    if product.image:
        await callback.message.answer_photo(
            photo=product.image,
            caption=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer(
            text=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    await callback.answer()
# @user_private_router.callback_query(F.data.startswith("taste_"), FavouritesState.choosing_taste)
# async def taste_selected(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
#     taste = callback.data.split("_")[1]
#     user_id = callback.from_user.id

#     stmt = select(Favourite).join(Product).filter(
#         Favourite.user_id == user_id,
#         Product.taste == taste,
#         Product.is_closed == False  # Добавляем условие для исключения скрытых товаров
#     ).options(selectinload(Favourite.product))
#     result = await session.execute(stmt)
#     favourite = result.scalar()

#     if not favourite:
#         await callback.message.answer("Товар с таким вкусом не найден в избранном.")
#         return

#     product = favourite.product
#     product_id = product.id

#     keyboard = [
#         [
#             InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
#             for i in range(1, 6)
#         ],
#         [
#             InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
#             for i in range(6, 11)
#         ],
#         [
#             InlineKeyboardButton(text="Более 10 шт.", callback_data="opt_")
#         ],
#         [
#             InlineKeyboardButton(text="Удалить", callback_data=f"d_fav_{product.id}"),
#             InlineKeyboardButton(text="Главная", callback_data="activate_start")
#         ],
#     ]
#     reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
#     stmt = select(Product.quantity).filter(Product.id == product_id)
#     result = await session.execute(stmt)
#     quantity_on_stock = result.scalar()
#     if quantity_on_stock is None:
#         await callback.message.answer("Товар не найден на складе.")
#         await callback.answer()
#         return
#     if quantity_on_stock < 0:
#         try:
#             await bot.send_message(USER_ID, f"Warning: Product '{product.name}' has a quantity less than 0!")
#         except Exception as e:
#             logging.error(f"Failed to send message to admin: {e}")
#     if quantity_on_stock < 1:
#         nali = "Только под заказ"
#     elif 0 < quantity_on_stock < 11:
#         nali = f"Количество товара: {quantity_on_stock}"
#     else:
#         nali = "Товар есть в наличие"
#     if product.image:
#         await callback.message.answer_photo(
#             photo=product.image,
#             caption=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
#             reply_markup=reply_markup
#         )
#     else:
#         await callback.message.answer(
#             text=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
#             reply_markup=reply_markup,
#             parse_mode="HTML"
#         )
#     await callback.answer()

def get_callback_btns2(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


@user_private_router.callback_query(F.data.startswith("izbra"))
async def izbra_selected(callback: types.CallbackQuery):
    await callback.message.answer("Это ваши избранные товары")
    await callback.answer()


@user_private_router.callback_query(F.data.startswith("d_fav"))
async def delete_from_favourites(callback: types.CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    stmt = delete(Favourite).where(Favourite.user_id == user_id, Favourite.product_id == product_id)
    await session.execute(stmt)
    await session.commit()

    await callback.message.answer("Товар удален из избранного.")
    await callback.answer()


@user_private_router.message(F.contact)
async def get_contact(message: types.Message):
    await message.answer(f"номер получен")
    await message.answer(str(message.contact))


@user_private_router.message(F.location)
async def get_location(message: types.Message):
    await message.answer(f"локация получена")
    await message.answer(str(message.location))




def get_callback_btns2(*, btns: dict[str, str], sizes: tuple[int] = (1,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


@user_private_router.message(F.text.lower() == "купить 🛒")
@user_private_router.message(Command("buy"))
async def buy_cmd(message: types.Message):
    is_subscribed = await check_subscription(message.from_user.id)
    if is_subscribed:
        await message.answer(
            text="🌬️Выберите необходимую категорию желаемого товара:",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Жидкости", callback_data='vape e-juice'),
                        InlineKeyboardButton(text="Одноразки", callback_data='odnorazki')
                    ],
                    [
                        InlineKeyboardButton(text="POD-системы", callback_data='podiki'),
                        InlineKeyboardButton(text="Снюс", callback_data='snus')
                    ]
                ]
            )
        )
    else:
        await message.answer("Подпишитесь на канал!", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
                [InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
            ]
        ))


@user_private_router.callback_query(F.data.in_({"in_stock", "pre_order"}))
async def purchase_option_selected(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await state.update_data(purchase_option=callback.data)
    data = await state.get_data()
    category = data.get('category')
    categories = {
        "vape e-juice": 1,
        "odnorazki": 2,
        "podiki": 3,
        "snus": 4
    }
    category_id = categories.get(category)
    if category_id is None:
        await callback.message.edit_text("Категория не найдена.")
        return

    purchase_option = data.get('purchase_option', 'in_stock')
    products = await orm_get_makers_by_category(category_id=category_id, session=session, in_stock=(purchase_option == 'in_stock'))
    btns = {product.maker: f"maker_{product.maker}" for product in products}
    await callback.message.edit_text(f"Выберите производителя:", reply_markup=get_callback_btns2(btns=btns))


@user_private_router.callback_query(F.data.in_({"vape e-juice", "odnorazki", "podiki", "snus"}))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    await state.update_data(category=callback.data)
    await callback.message.edit_text(
        text="🌬️Выберите вариант покупки:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Есть в наличии", callback_data='in_stock')
                ],
                # [
                #     InlineKeyboardButton(text="Под заказ", callback_data='pre_order')
                # ]
            ]
        )
    )


@user_private_router.callback_query(F.data.startswith("maker_"))
async def maker_products(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    maker = callback.data.split("_")[1]
    data = await state.get_data()
    purchase_option = data.get('purchase_option', 'in_stock')
    products = await get_products_with_tastes(maker=maker, session=session, in_stock=(purchase_option == 'in_stock'))
    
    if not products:
        await callback.message.edit_text(f"Нет продуктов производителя {maker}.")
        return
    
    btns = {f"{product.name} ({product.taste})": f"product_{product.id}" for product in products if product.quantity > 0}
    
    if not btns:
        await callback.message.edit_text(f"Нет доступных продуктов производителя {maker}.")
        return
    
    await callback.message.edit_text(f"Выберите товар производителя:", reply_markup=get_callback_btns2(btns=btns))

@user_private_router.callback_query(F.data.startswith("product_"))
async def product_details(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    product_id = int(callback.data.split("_")[1])
    product = await orm_get_product(session=session, product_id=product_id)
    
    if not product or product.is_closed:  # Проверяем, существует ли товар и не скрыт ли он
        await callback.message.answer("Товар недоступен.")
        await callback.answer()
        return

    keyboard = [
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(1, 6)
        ],
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(6, 11)
        ],
        [
            InlineKeyboardButton(text="Более 10 шт.", callback_data="opt_")
        ],
        [
            InlineKeyboardButton(text="Избранное", callback_data=f"favourite_{product.id}")
        ],
        [
            InlineKeyboardButton(text="Главная", callback_data="activate_start")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    stmt = select(Product.quantity).filter(Product.id == product_id)
    result = await session.execute(stmt)
    quantity_on_stock = result.scalar()
    if quantity_on_stock is None:
        await callback.message.answer("Товар не найден на складе.")
        await callback.answer()
        return
    if quantity_on_stock < 0:
        try:
            await bot.send_message(USER_ID, f"Warning: Product '{product.name}' has a quantity less than 0!")
        except Exception as e:
            logging.error(f"Failed to send message to admin: {e}")
    if quantity_on_stock < 1:
        nali = "Только под заказ"
    elif 0 < quantity_on_stock < 11:
        nali = f"Количество товара: {quantity_on_stock}"
    else:
        nali = "Товар есть в наличие"
    if product.image:
        await callback.message.answer_photo(
            photo=product.image,
            caption=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer(
            text=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    await callback.answer()

@user_private_router.callback_query(F.data.startswith("buy_"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    data = callback.data.split("_")
    product_id = int(data[1])
    quantity = int(data[2])

    # Получаем информацию о товаре из базы данных
    stmt = select(Product).filter(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar()

    if not product:
        await callback.message.answer("Товар не найден.")
        await callback.answer()
        return

    # Добавляем товар в корзину
    cart_item = CartItem(user_id=callback.from_user.id, product_id=product_id, quantity=quantity, price_at_time=product.price)
    session.add(cart_item)
    await session.commit()

    # Отправляем сообщение о том, что товар был успешно добавлен в корзину
    await callback.message.answer("Товар успешно добавлен в корзину!")

    # Отправляем начальные категории для продолжения покупок
    await callback.message.answer(
        text="🌬️Выберите необходимую категорию желаемого товара:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Жидкости", callback_data='vape e-juice'),
                    InlineKeyboardButton(text="Одноразки", callback_data='odnorazki')
                ],
                [
                    InlineKeyboardButton(text="POD-системы", callback_data='podiki'),
                    InlineKeyboardButton(text="Снюс", callback_data='snus')
                ]
            ]
        )
    )
    await callback.answer()

@user_private_router.callback_query(F.data.startswith("favourite_"))
async def add_to_favourites(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    stmt = select(Favourite).filter(Favourite.user_id == user_id, Favourite.product_id == product_id)
    result = await session.execute(stmt)
    existing_favourite = result.scalar()
    if existing_favourite:
        await callback.message.answer("Товар уже в избранном!")
    else:
        favourite = Favourite(user_id=user_id, product_id=product_id)
        session.add(favourite)
        await session.commit()
        await callback.message.answer("Успешно добавлено в избранное!")
    await callback.answer()


@user_private_router.callback_query(F.data.startswith("opt_"))
async def opt_product(callback: CallbackQuery):
    await callback.message.answer("Для заказа товара более 10 единиц свяжитесь с нашим менеджером - @SmokyScreenShop | Время работы 10:00-22:00 ")
    await callback.answer()


# @user_private_router.callback_query(F.data.startswith("buy_"))
# async def buy_product(callback: CallbackQuery, bot: Bot, session: AsyncSession):
#     data = callback.data.split("_")
#     product_id = int(data[1])
#     quantity = int(data[2])

#     stmt = select(Product.quantity).filter(Product.id == product_id)
#     result = await session.execute(stmt)
#     quantity_on_stock = result.scalar()

#     if quantity_on_stock is None:
#         await callback.message.answer("Товар не найден на складе.")
#         await callback.answer()
#         return

#     product = await orm_get_product(session, product_id=product_id)
#     if product:
#         total_price = product.price * quantity
#         keyboard = [
#             [
#                 InlineKeyboardButton(text="Самовывоз", callback_data=f"pickup_{product_id}_{quantity}_{total_price}_{product.name}"),
#             ],
#             [
#                 (InlineKeyboardButton(text="Доставка", callback_data=f"delivery_{product_id}_{quantity}_{total_price}_{product.name}"))
#             ]
#         ]
#         reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

#         if quantity > quantity_on_stock:
#             await callback.message.answer(
#                 f"В настоящее время товар в требуемом количестве отсутствует на нашем складе. На складе {quantity_on_stock} шт.\nМы зарегистрируем ваш заказ и свяжемся с вами, как только товар поступит к нам на склад.\nВозможны отклонения со временем.\nВыберите способ получения:",
#                 reply_markup=reply_markup
#             )
#         else:
#             await callback.message.answer("Выберите способ получения:", reply_markup=reply_markup)

#     await callback.answer()


# class DeliveryState(StatesGroup):
#     waiting_for_pickup_datetime = State()
#     waiting_for_datetime = State()
#     waiting_for_payment_method = State()
#     waiting_for_promo_code = State()
#     waiting_for_user_confirmation = State()


# @user_private_router.callback_query(F.data.startswith("pickup_"))
# async def pickup_product(callback: CallbackQuery, state: FSMContext):
#     data = callback.data.split("_")
#     if len(data) < 5:
#         await callback.answer("Ошибка: некорректные данные")
#         return
    
#     product_id = int(data[1])
#     quantity = int(data[2])
#     total_price = int(float(data[3]))
#     name = data[4]
    
#     total_price_with_fee = int(total_price)
    
#     payload = f"С_{product_id}_{quantity}_{total_price_with_fee}_{name}"
#     address = "Самовывоз"
    
#     await callback.message.answer("Пожалуйста, укажите дату и время самовывоза в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя самовывоза с 10:00 до 20:00.")
    
#     await state.update_data(product_id=product_id, quantity=quantity, total_price=total_price_with_fee, name=name, payload=payload, address=address)
    
#     await state.set_state(DeliveryState.waiting_for_pickup_datetime)
#     await callback.answer()


# @user_private_router.message(StateFilter(DeliveryState.waiting_for_pickup_datetime))
# async def pickup_datetime_received(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         pickup_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return
    
#     current_time = datetime.datetime.now()
#     if pickup_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return
    
#     if not (10 <= pickup_datetime.hour < 22):
#         await message.answer("Время самовывоза должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return
    
#     data = await state.get_data()
#     product_id = data['product_id']
#     quantity = data['quantity']
#     total_price = data['total_price']
#     name = data['name']
#     payload = data['payload']
#     address = data['address']
    
#     await state.update_data(pickup_datetime=pickup_datetime)
    
#     await message.answer("Адрес самовывоза\nВелит - офисный  центр\nУлица 40 лет Победы, 26")
    
#     try:
#         await bot.send_location(chat_id=message.chat.id, latitude=OFFICE_COORDS[0], longitude=OFFICE_COORDS[1])
#     except TelegramError as e:
#         print(f"Ошибка при отправке геопозиции: {e}")
    
#     stmt = select(Product.quantity).filter(Product.id == product_id)
#     result = await session.execute(stmt)
#     quantity_on_stock = result.scalar()
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="ЮКасса", callback_data="payment_yookassa")],
#         [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
#         [InlineKeyboardButton(text="Промокод", callback_data="payment_promo")],
#     ])
#     await message.answer("Выберите способ оплаты:", reply_markup=keyboard)
#     await state.set_state(DeliveryState.waiting_for_payment_method)


# @user_private_router.callback_query(F.data.startswith("delivery_"))
# async def delivery_product(callback: CallbackQuery, bot: Bot):
#     data = callback.data.split("_")
#     if len(data) < 5:
#         await callback.answer("Ошибка: некорректные данные")
#         return
    
#     product_id = int(data[1])
#     quantity = int(data[2])
#     total_price = int(float(data[3]))
#     name = data[4]
    
#     keyboard = [
#         [
#             InlineKeyboardButton(text="Автозаводский", callback_data=f"avto_{product_id}_{quantity}_{total_price}_{name}"),
#             InlineKeyboardButton(text="Центральный", callback_data=f"centr_{product_id}_{quantity}_{total_price}_{name}"),
#         ],
#         [
#             InlineKeyboardButton(text="Комсомольский", callback_data=f"komsomol_{product_id}_{quantity}_{total_price}_{name}"),
#             InlineKeyboardButton(text="Шлюзовой", callback_data=f"shlyuz_{product_id}_{quantity}_{total_price}_{name}")
#         ]
#     ]
#     reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
#     await callback.message.answer(text="Выберите ваш район:", reply_markup=reply_markup)
#     await callback.answer()


# @user_private_router.callback_query(F.data.startswith(("avto_", "centr_", "komsomol_", "shlyuz_")))
# async def district_selected(callback: CallbackQuery, state: FSMContext):
#     data = callback.data.split("_")
#     if len(data) < 5:
#         await callback.answer("Ошибка: некорректные данные")
#         return
    
#     district = data[0]
#     product_id = int(data[1])
#     quantity = int(data[2])
#     total_price = int(float(data[3]))
#     name = data[4]
    
#     await state.update_data(product_id=product_id, quantity=quantity, total_price=total_price, name=name, district=district, address="неизвестно", payload="")  # Добавляем payload
#     await callback.message.answer("Пожалуйста, укажите дату и время желаемой доставки в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя доставки с 10:00 до 20:00.")
#     await state.set_state(DeliveryState.waiting_for_datetime)
#     await callback.answer()



# @user_private_router.message(StateFilter(DeliveryState.waiting_for_datetime))
# async def datetime_received(message: Message, state: FSMContext, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         delivery_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return
    
#     current_time = datetime.datetime.now()
#     if delivery_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return
    
#     if not (10 <= delivery_datetime.hour < 22):
#         await message.answer("Время доставки должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return

#     if (delivery_datetime - current_time).total_seconds() < 3 * 3600:
#         await message.answer("Время доставки должно быть не менее чем через 3 часа от текущего времени. Пожалуйста, укажите корректное время.")
#         return

#     data = await state.get_data()
#     product_id = data['product_id']
#     quantity = data['quantity']
#     total_price = data['total_price']
#     name = data['name']
#     district = data['district']

#     await state.update_data(delivery_datetime=delivery_datetime)
#     stmt = select(Product.quantity).filter(Product.id == product_id)
#     result = await session.execute(stmt)
#     quantity_on_stock = result.scalar()
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="ЮКасса", callback_data="payment_yookassa")],
#         [InlineKeyboardButton(text="Промокод", callback_data="payment_promo")],
#     ])
#     await message.answer("Выберите способ оплаты:", reply_markup=keyboard)
#     await state.set_state(DeliveryState.waiting_for_payment_method)




# @user_private_router.callback_query(F.data == "payment_na_meste", StateFilter(DeliveryState.waiting_for_payment_method))
# async def payment_na_meste_selected(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     user_id = callback.from_user.id
#     product_id = data['product_id']
#     quantity = data['quantity']
#     total_price = data['total_price']
#     name = data['name']
#     address = data['address']
#     pickup_datetime = data.get('pickup_datetime')
#     delivery_datetime = data.get('delivery_datetime')
#     order_id = generate_order_id()

#     await state.update_data(order_id=order_id)

#     await callback.message.answer(f"Подтвердите ваш заказ:\n"
#                                   f"Товар: {name}\n"
#                                   f"Количество: {quantity}\n"
#                                   f"Общая цена: {total_price} руб.\n"
#                                   f"Адрес: {address}\n"
#                                   f"Время получения: {pickup_datetime or delivery_datetime}\n"
#                                   f"Для подтверждения введите 'Да'.")

#     await state.set_state(DeliveryState.waiting_for_user_confirmation)
#     await callback.answer()


# @user_private_router.message(StateFilter(DeliveryState.waiting_for_user_confirmation))
# async def user_confirmation_received(message: Message, state: FSMContext, session: AsyncSession):
#     if message.text.lower() == "да":
#         data = await state.get_data()
#         order_id = data['order_id']
#         user_id = message.from_user.id
#         product_id = data['product_id']
#         quantity = data['quantity']
#         total_price = data['total_price']
#         name = data['name']
#         address = data['address']
#         pickup_datetime = data.get('pickup_datetime')
#         delivery_datetime = data.get('delivery_datetime')

#         stmt = select(User).where(User.user_id == user_id)
#         result = await session.execute(stmt)
#         user = result.scalar_one_or_none()
#         referrer_id = user.referrer_id if user else None

#         product = await orm_get_product(session, product_id)
#         if not product:
#             await message.answer("Ошибка: продукт не найден.")
#             return

#         new_order = Order(
#             product_id=product_id,
#             price=total_price,
#             quantity=quantity,
#             name=name,
#             maker=product.maker,
#             taste=data.get('taste', ''),
#             user_id=user_id,
#             referrer_id=referrer_id,
#             order_number=order_id,
#             payment_status="Не оплачен",
#             order_status="В обработке"
#         )

#         session.add(new_order)
#         await session.commit()

#         await message.answer(f"Ваш заказ (ID: {order_id}) принят. Оплата будет произведена при получении.")

#         msg_ad = (f"Новый заказ оплаты на месте!\n"
#                   f"Пользователь ID: {user_id}\n"
#                   f"Товар: {name}\n"
#                   f"Количество: {quantity}\n"
#                   f"Общая цена: {total_price} руб.\n"
#                   f"Адрес: {address}\n"
#                   f"Время получения: {pickup_datetime or delivery_datetime}")

#         await bot.send_message(USER_ID, msg_ad)

#         try:
#             await update_product_quantity(session, product_id, quantity)
#             # await update_user_spent(session, user_id, total_price)
#         except ValueError as e:
#             await message.answer(f"Ошибка при обновлении данных: {e}")

#         await state.clear()
#     else:
#         await message.answer("Заказ не подтвержден. Пожалуйста, введите 'Да' для подтверждения.")

# def calculate_delivery_cost(district, total_price_in_kopecks):
#     total_price = total_price_in_kopecks / 100  # Перевод в рубли
#     delivery_cost = 0

#     if district == "avto":
#         if total_price < 1000:
#             delivery_cost = 5000  # 50 рублей в копейках
#     elif district == "centr":
#         if total_price < 2000:
#             delivery_cost = 10000  # 100 рублей в копейках
#     elif district == "komsomol":
#         if total_price < 3000:
#             delivery_cost = 15000  # 150 рублей в копейках
#     elif district == "shlyuz":
#         if total_price < 3500:
#             delivery_cost = 17500  # 175 рублей в копейках

#     return delivery_cost

# @user_private_router.callback_query(F.data == "payment_yookassa", StateFilter(DeliveryState.waiting_for_payment_method))
# async def payment_yookassa_selected(callback: CallbackQuery, state: FSMContext, bot: Bot):
#     data = await state.get_data()
#     product_id = data['product_id']
#     quantity = data['quantity']
#     total_price = data['total_price']
#     name = data['name']
#     address = data.get('address', 'неизвестно')  # Используем get для безопасного доступа
#     pickup_datetime = data.get('pickup_datetime')
#     delivery_datetime = data.get('delivery_datetime')
#     promo_code = data.get('promo_code', '')

#     method = "С" if pickup_datetime else "Д"
#     datetime_str = pickup_datetime.strftime('%d%m%Y%H%M') if pickup_datetime else delivery_datetime.strftime('%d%m%Y%H%M')
#     payload = f"{method}_{product_id}_{quantity}_{total_price}_{name}_{address}_{datetime_str}_{promo_code}"
    
#     if len(payload) > 128:
#         payload = payload[:128]
    
#     logging.info(f"Payload: {payload}")

#     await order(callback.message, bot, total_price, name, payload, address, pickup_datetime or delivery_datetime, promo_code)
#     await callback.answer


# @user_private_router.callback_query(F.data.startswith("payment_promo"), StateFilter(DeliveryState.waiting_for_payment_method))
# async def payment_method_selected(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Введите промокод:")
#     await state.set_state(DeliveryState.waiting_for_promo_code)
#     await callback.answer()


# @user_private_router.message(StateFilter(DeliveryState.waiting_for_promo_code))
# async def promo_code_received(message: Message, state: FSMContext, session: AsyncSession):
#     promo_code = message.text
#     data = await state.get_data()
#     total_price = data['total_price']
#     name = data['name']
#     address = data['address']
#     pickup_datetime = data.get('pickup_datetime')
#     delivery_datetime = data.get('delivery_datetime')
    
#     success, new_total_price = await activate_promo_code(session, promo_code, total_price)
#     if success:
#         await message.answer(f"Промокод применен. Новая сумма: {new_total_price} руб.")
#     else:
#         await message.answer("Промокод не найден.")
    
#     method = "С" if pickup_datetime else "Д"
#     datetime_str = pickup_datetime.strftime('%d%m%Y%H%M') if pickup_datetime else delivery_datetime.strftime('%d%m%Y%H%M')
#     payload = f"{method}_{data['product_id']}_{data['quantity']}_{new_total_price}_{name}_{address}_{datetime_str}_{promo_code}"
    
#     await state.update_data(total_price=new_total_price, payload=payload)
#     await order(message, bot, new_total_price, name, payload, address, pickup_datetime or delivery_datetime, promo_code)
#     await state.set_state(DeliveryState.waiting_for_payment_method)


# async def activate_promo_code(session: AsyncSession, promo_code: str, total_price: int) -> tuple[bool, int]:
#     stmt = select(Promocode).filter(Promocode.name == promo_code)
#     result = await session.execute(stmt)
#     promo = result.scalar_one_or_none()
    
#     if promo:
#         if promo.discount_type == 'PERCENT':
#             discount = total_price * (promo.discount_amount / 100)
#         else:
#             discount = promo.discount_amount
#         total_price -= discount
#         await delete_promo_code(session, promo_code)
#         return True, total_price
#     else:
#         return False, total_price


# async def order(message: Message, bot: Bot, price, name, payload, address, delivery_datetime, promo_code):
#     try:
#         total_price_in_kopecks = int(price * 100)
        
#         method = payload.split("_")[0]
#         need_shipping_address = method == "Д"

#         delivery_cost = 0
#         if method == "Д":
#             parts = payload.split("_")
#             if len(parts) < 6:
#                 await message.answer("Ошибка: некорректные данные в payload")
#                 return
#             district = parts[5]
#             delivery_cost = calculate_delivery_cost(district, total_price_in_kopecks)

#         prices = [
#             LabeledPrice(label=name, amount=total_price_in_kopecks),
#             LabeledPrice(label="Комиссия", amount=int(total_price_in_kopecks * 0.03))
#         ]

#         if method == "Д" and delivery_cost > 0:
#             prices.append(LabeledPrice(label="Стоимость доставки", amount=delivery_cost))

#         await bot.send_invoice(
#             chat_id=message.chat.id,
#             title=name[:32],
#             description=f"Заказ: {name[:255]}\n\nВремя: {delivery_datetime.strftime('%d.%m.%Y %H:%M')}",
#             payload=payload,
#             provider_token="381764678:TEST:91259",
#             currency="RUB",
#             prices=prices,
#             max_tip_amount=500000,
#             suggested_tip_amounts=[2500, 5000, 10000, 15000],
#             start_parameter="12331232",
#             provider_data=None,
#             photo_url="",
#             photo_size=200,
#             photo_height=200,
#             photo_width=200,
#             need_name=True,
#             need_phone_number=True,
#             need_email=False,
#             need_shipping_address=need_shipping_address,
#             send_phone_number_to_provider=False,
#             send_email_to_provider=False,
#             is_flexible=False,
#             disable_notification=False,
#             protect_content=False,
#             reply_to_message_id=None,
#             allow_sending_without_reply=True,
#             reply_markup=None,
#             request_timeout=60
#         )

#     except Exception as e:
#         await message.answer(f"Ошибка при отправке инвойса: {e}")
#         logging.error(f"Ошибка при отправке инвойса: {e}")


# @user_private_router.pre_checkout_query()
# async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
#     await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# def generate_order_id():
#     timestamp = datetime.datetime.now().strftime("%Y%m%d") 
#     random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))  
#     order_id = f"ORD-{timestamp}-{random_part}"
#     return order_id


# @user_private_router.message(F.content_type == "successful_payment")
# async def successful_payment(message: Message, state: FSMContext, session: AsyncSession):
#     total_amount = message.successful_payment.total_amount // 100
#     currency = message.successful_payment.currency
#     payload = message.successful_payment.invoice_payload
#     logging.info(f"Payload: {payload}")
#     parts = payload.split("_")
#     if len(parts) >= 8:
#         method = parts[0]
#         product_id = int(parts[1])
#         quantity = int(parts[2])
#         total_price = int(float(parts[3]))
#         name = parts[4]
#         address = parts[5]
#         delivery_datetime_str = parts[6]
#         promo_code = parts[7]
#         try:
#             delivery_datetime = datetime.datetime.strptime(delivery_datetime_str, '%d%m%Y%H%M')
#         except ValueError:
#             delivery_datetime = "неизвестно"
#     else:
#         method = "неизвестно"
#         quantity = "неизвестно"
#         total_price = total_amount
#         name = "неизвестно"
#         address = "неизвестно"
#         delivery_datetime = "неизвестно"
#         promo_code = "неизвестно"

#     order_info = message.successful_payment.order_info
#     user_name = order_info.name if order_info else "неизвестно"
#     user_phone = order_info.phone_number if order_info else "неизвестно"
#     user_address = order_info.shipping_address.street_line1 if order_info and order_info.shipping_address else "неизвестно"

#     order_id = generate_order_id()
#     msg = f"Спасибо за покупку! ❤️\nВаш товар: <b>{name}</b>!\nНомер заказа: <b>{order_id}</b>.\nИтоговая цена составляет: <b>{total_amount} {currency}</b>\n\nАккаунт тех. поддержки - <b>@SmokyScreenShop</b> | Время работы 10:00-22:00"
#     await message.answer(msg, parse_mode="HTML")

#     if method == "С":
#         msg_ad = (f"Новый заказ!\nНомер заказа: <b>{order_id}</b>\nТовар: <b>{name}</b>\nКоличество: <b>{quantity}</b>\n"
#                   f"Итоговая цена составляет <b>{total_amount} {currency}</b>\nМетод получения товара: самовывоз\n"
#                   f"Адрес самовывоза: <b>{address}</b>\nВремя самовывоза: <b>{delivery_datetime}</b>\n"
#                   f"Контактные данные:\nИмя: <b>{user_name}</b>\nТелефон: <b>{user_phone}</b>")
#     else:
#         msg_ad = (f"Новый заказ!\nНомер заказа: <b>{order_id}</b>\nТовар: <b>{name}</b>\nКоличество: <b>{quantity}</b>\n"
#                   f"Итоговая цена составляет <b>{total_amount} {currency}</b>\nМетод получения товара: доставка\n"
#                   f"Адрес доставки: <b>{user_address}</b>\nВремя доставки: <b>{delivery_datetime}</b>\n"
#                   f"Контактные данные:\nИмя: <b>{user_name}</b>\nТелефон: <b>{user_phone}</b>")

#     await bot.send_message(USER_ID, msg_ad, parse_mode="HTML")

#     user_id = message.from_user.id
#     stmt = select(User).where(User.user_id == user_id)
#     result = await session.execute(stmt)
#     user = result.scalar_one_or_none()
#     referrer_id = user.referrer_id if user else None

#     product = await orm_get_product(session, product_id)
#     if not product:
#         await message.answer("Ошибка: продукт не найден.")
#         return

#     new_order = Order(
#         product_id=product_id,
#         price=total_price,
#         quantity=quantity,
#         name=name,
#         maker=product.maker,
#         taste=promo_code,
#         user_id=user_id,
#         referrer_id=referrer_id,
#         order_number=order_id,
#         payment_status="Оплачен",
#         order_status="В обработке"
#     )

#     session.add(new_order)
#     await session.commit()

#     try:
#         await update_product_quantity(session, product_id, quantity)
#         # await update_user_spent(session, user_id, total_amount)
#     except ValueError as e:
#         # await message.answer(f"Ошибка при обновлении данных: {e}")
#         pass

#     await delete_promo_code(session, promo_code)





class DeliveryState(StatesGroup):
    waiting_for_pickup_datetime = State()
    waiting_for_datetime = State()
    waiting_for_user_confirmation = State()

@user_private_router.callback_query(F.data.startswith("product_"))
async def product_details(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    product_id = int(callback.data.split("_")[1])
    product = await orm_get_product(session=session, product_id=product_id)
    
    if not product or product.is_closed:  # Проверяем, существует ли товар и не скрыт ли он
        await callback.message.answer("Товар недоступен.")
        await callback.answer()
        return

    keyboard = [
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(1, 6)
        ],
        [
            InlineKeyboardButton(text=f"{i} шт.", callback_data=f"buy_{product.id}_{i}")
            for i in range(6, 11)
        ],
        [
            InlineKeyboardButton(text="Более 10 шт.", callback_data="opt_")
        ],
        [
            InlineKeyboardButton(text="Избранное", callback_data=f"favourite_{product.id}")
        ],
        [
            InlineKeyboardButton(text="Главная", callback_data="activate_start")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    stmt = select(Product.quantity).filter(Product.id == product_id)
    result = await session.execute(stmt)
    quantity_on_stock = result.scalar()
    if quantity_on_stock is None:
        await callback.message.answer("Товар не найден на складе.")
        await callback.answer()
        return
    if quantity_on_stock < 0:
        try:
            await bot.send_message(USER_ID, f"Warning: Product '{product.name}' has a quantity less than 0!")
        except Exception as e:
            logging.error(f"Failed to send message to admin: {e}")
    if quantity_on_stock < 1:
        nali = "Только под заказ"
    elif 0 < quantity_on_stock < 11:
        nali = f"Количество товара: {quantity_on_stock}"
    else:
        nali = "Товар есть в наличие"
    if product.image:
        await callback.message.answer_photo(
            photo=product.image,
            caption=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup
        )
    else:
        await callback.message.answer(
            text=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅ {nali}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    await callback.answer()

@user_private_router.callback_query(F.data.startswith("buy_"))
async def add_to_cart(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    data = callback.data.split("_")
    product_id = int(data[1])
    quantity = int(data[2])

    # Получаем информацию о товаре из базы данных
    stmt = select(Product).filter(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar()

    if not product:
        await callback.message.answer("Товар не найден.")
        await callback.answer()
        return

    # Добавляем товар в корзину
    cart_item = CartItem(user_id=callback.from_user.id, product_id=product_id, quantity=quantity, price_at_time=product.price)
    session.add(cart_item)
    await session.commit()

    # Отправляем сообщение о том, что товар был успешно добавлен в корзину
    await callback.message.answer("Товар успешно добавлен в корзину!")

    # Отправляем начальные категории для продолжения покупок
    await callback.message.answer(
        text="🌬️Выберите необходимую категорию желаемого товара:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Жидкости", callback_data='vape e-juice'),
                    InlineKeyboardButton(text="Одноразки", callback_data='odnorazki')
                ],
                [
                    InlineKeyboardButton(text="POD-системы", callback_data='podiki'),
                    InlineKeyboardButton(text="Снюс", callback_data='snus')
                ]
            ]
        )
    )
    await callback.answer()

# @user_private_router.message(F.text.lower() == "купить 🛒")
# @user_private_router.message(Command("buy"))
# async def buy_cmd(message: types.Message):
#     is_subscribed = await check_subscription(message.from_user.id)
#     if is_subscribed:
#         await message.answer(
#             text="🌬️Выберите необходимую категорию желаемого товара:",
#             reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=[
#                     [
#                         InlineKeyboardButton(text="Жидкости", callback_data='vape e-juice'),
#                         InlineKeyboardButton(text="Одноразки", callback_data='odnorazki')
#                     ],
#                     [
#                         InlineKeyboardButton(text="POD-системы", callback_data='podiki'),
#                         InlineKeyboardButton(text="Снюс", callback_data='snus')
#                     ]
#                 ]
#             )
#         )
#     else:
#         await message.answer("Подпишитесь на канал!", reply_markup=InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="Телеграмм канал", url='https://t.me/smokyscreen')],
#                 [InlineKeyboardButton(text="Проверить", callback_data='activate_start')]
#             ]
#         ))

# @user_private_router.message(F.text.lower() == "корзина 🛒")
# @user_private_router.message(Command("cart"))
# async def view_cart(message: types.Message, session: AsyncSession):
#     user_id = message.from_user.id
#     stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
#     result = await session.execute(stmt)
#     cart_items = result.scalars().all()

#     if not cart_items:
#         await message.answer("Ваша корзина пуста.")
#         return

#     cart_text = "Ваша корзина:\n\n"
#     total_price = 0

#     for item in cart_items:
#         product = item.product
#         item_total_price = item.quantity * item.price_at_time
#         cart_text += f"{product.name} - {item.quantity} шт. - {item_total_price} руб.\n"
#         total_price += item_total_price

#     cart_text += f"\nИтого: {total_price} руб."

#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart"),
#                 InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")
#             ]
#         ]
#     )

#     await message.answer(cart_text, reply_markup=keyboard)

# @user_private_router.callback_query(F.data == "clear_cart")
# async def clear_cart(callback: CallbackQuery, session: AsyncSession):
#     user_id = callback.from_user.id
#     stmt = delete(CartItem).where(CartItem.user_id == user_id)
#     await session.execute(stmt)
#     await session.commit()

#     await callback.message.answer("Корзина очищена.")
#     await callback.answer()

# @user_private_router.callback_query(F.data == "checkout")
# async def checkout(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     user_id = callback.from_user.id
#     stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
#     result = await session.execute(stmt)
#     cart_items = result.scalars().all()

#     if not cart_items:
#         await callback.message.answer("Ваша корзина пуста.")
#         await callback.answer()
#         return

#     total_price = sum(item.quantity * item.price_at_time for item in cart_items)
#     product_id = cart_items[0].product_id  # Assuming only one product for simplicity
#     quantity = cart_items[0].quantity
#     name = cart_items[0].product.name
#     address = "Адрес самовывоза\nВелит - офисный центр\nУлица 40 лет Победы, 26"

#     await state.update_data(
#         product_id=product_id,
#         quantity=quantity,
#         total_price=total_price,
#         name=name,
#         address=address
#     )

#     await callback.message.answer("Выберите способ получения заказа:", reply_markup=InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="Самовывоз", callback_data="pickup"),
#                 InlineKeyboardButton(text="Доставка", callback_data="delivery")
#             ]
#         ]
#     ))
#     await state.set_state(DeliveryState.waiting_for_pickup_datetime)
#     await callback.answer()

# @user_private_router.callback_query(F.data == "pickup")
# async def pickup_selected(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Пожалуйста, укажите дату и время самовывоза в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя самовывоза с 10:00 до 20:00.")
#     await state.set_state(DeliveryState.waiting_for_pickup_datetime)
#     await callback.answer()

# @user_private_router.callback_query(F.data == "delivery")
# async def delivery_selected(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Пожалуйста, укажите дату и время доставки в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя доставки с 10:00 до 20:00.")
#     await state.set_state(DeliveryState.waiting_for_datetime)
#     await callback.answer()

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_pickup_datetime))
# async def pickup_datetime_received(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         pickup_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return

#     current_time = datetime.datetime.now()
#     if pickup_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return

#     if not (10 <= pickup_datetime.hour < 22):
#         await message.answer("Время самовывоза должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return

#     await state.update_data(pickup_datetime=pickup_datetime)
#     await message.answer("Адрес самовывоза\nВелит - офисный центр\nУлица 40 лет Победы, 26")

#     try:
#         await bot.send_location(chat_id=message.chat.id, latitude=OFFICE_COORDS[0], longitude=OFFICE_COORDS[1])
#     except TelegramError as e:
#         print(f"Ошибка при отправке геопозиции: {e}")

#     await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
#     ]))
#     await state.set_state(DeliveryState.waiting_for_user_confirmation)

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_datetime))
# async def delivery_datetime_received(message: Message, state: FSMContext, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         delivery_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return

#     current_time = datetime.datetime.now()
#     if delivery_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return

#     if not (10 <= delivery_datetime.hour < 22):
#         await message.answer("Время доставки должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return

#     if (delivery_datetime - current_time).total_seconds() < 3 * 3600:
#         await message.answer("Время доставки должно быть не менее чем через 3 часа от текущего времени. Пожалуйста, укажите корректное время.")
#         return

#     await state.update_data(delivery_datetime=delivery_datetime)
#     await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
#     ]))
#     await state.set_state(DeliveryState.waiting_for_user_confirmation)

# @user_private_router.callback_query(F.data == "payment_na_meste", StateFilter(DeliveryState.waiting_for_user_confirmation))
# async def payment_na_meste_selected(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     logging.info(f"Data from state: {data}")
#     if 'product_id' not in data or 'quantity' not in data or 'total_price' not in data or 'name' not in data or 'address' not in data:
#         await callback.message.answer("Произошла ошибка: данные о заказе отсутствуют. Пожалуйста, попробуйте снова.")
#         await state.clear()
#         await callback.answer()
#         return

#     user_id = callback.from_user.id
#     product_id = data['product_id']
#     quantity = data['quantity']
#     total_price = data['total_price']
#     name = data['name']
#     address = data['address']
#     pickup_datetime = data.get('pickup_datetime')
#     delivery_datetime = data.get('delivery_datetime')
#     order_id = generate_order_id()

#     await state.update_data(order_id=order_id)

#     await callback.message.answer(f"Подтвердите ваш заказ:\n"
#                                   f"Товар: {name}\n"
#                                   f"Количество: {quantity}\n"
#                                   f"Общая цена: {total_price} руб.\n"
#                                   f"Адрес: {address}\n"
#                                   f"Время получения: {pickup_datetime or delivery_datetime}\n"
#                                   f"Для подтверждения введите 'Да'.")

#     await state.set_state(DeliveryState.waiting_for_user_confirmation)
#     await callback.answer()

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_user_confirmation))
# async def user_confirmation_received(message: Message, state: FSMContext, session: AsyncSession):
#     if message.text.lower() == "да":
#         data = await state.get_data()
#         order_id = data['order_id']
#         user_id = message.from_user.id
#         product_id = data['product_id']
#         quantity = data['quantity']
#         total_price = data['total_price']
#         name = data['name']
#         address = data['address']
#         pickup_datetime = data.get('pickup_datetime')
#         delivery_datetime = data.get('delivery_datetime')

#         stmt = select(User).where(User.user_id == user_id)
#         result = await session.execute(stmt)
#         user = result.scalar_one_or_none()
#         referrer_id = user.referrer_id if user else None

#         product = await orm_get_product(session, product_id)
#         if not product:
#             await message.answer("Ошибка: продукт не найден.")
#             return

#         new_order = Order(
#             product_id=product_id,
#             price=total_price,
#             quantity=quantity,
#             name=name,
#             maker=product.maker,
#             taste=data.get('taste', ''),
#             user_id=user_id,
#             referrer_id=referrer_id,
#             order_number=order_id,
#             payment_status="Не оплачен",
#             order_status="В обработке"
#         )

#         session.add(new_order)
#         await session.commit()

#         await message.answer(f"Ваш заказ (ID: {order_id}) принят. Оплата будет произведена при получении.")

#         msg_ad = (f"Новый заказ оплаты на месте!\n"
#                   f"Пользователь ID: {user_id}\n"
#                   f"Товар: {name}\n"
#                   f"Количество: {quantity}\n"
#                   f"Общая цена: {total_price} руб.\n"
#                   f"Адрес: {address}\n"
#                   f"Время получения: {pickup_datetime or delivery_datetime}")

#         await bot.send_message(USER_ID, msg_ad)

#         try:
#             await update_product_quantity(session, product_id, quantity)
#             # await update_user_spent(session, user_id, total_price)
#         except ValueError as e:
#             await message.answer(f"Ошибка при обновлении данных: {e}")

#         await state.clear()
#     else:
#         await message.answer("Заказ не подтвержден. Пожалуйста, введите 'Да' для подтверждения.")

# def generate_order_id():
#     timestamp = datetime.datetime.now().strftime("%Y%m%d") 
#     random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))  
#     order_id = f"ORD-{timestamp}-{random_part}"
#     return order_id



# @user_private_router.message(F.text.lower() == "корзина 🛒")
# @user_private_router.message(Command("cart"))
# async def view_cart(message: types.Message, session: AsyncSession):
#     user_id = message.from_user.id
#     stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
#     result = await session.execute(stmt)
#     cart_items = result.scalars().all()

#     if not cart_items:
#         await message.answer("Ваша корзина пуста.")
#         return

#     cart_text = "Ваша корзина:\n\n"
#     total_price = 0
#     grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

#     for item in cart_items:
#         product = item.product
#         item_total_price = item.quantity * item.price_at_time
#         grouped_items[product.id]["quantity"] += item.quantity
#         grouped_items[product.id]["total_price"] += item_total_price
#         total_price += item_total_price

#     for product_id, details in grouped_items.items():
#         product = next(item.product for item in cart_items if item.product.id == product_id)
#         cart_text += f"{product.name} - {details['quantity']} шт. - {details['total_price']} руб.\n"

#     cart_text += f"\nИтого: {total_price} руб."

#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart"),
#                 InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")
#             ]
#         ]
#     )

#     await message.answer(cart_text, reply_markup=keyboard)

# @user_private_router.callback_query(F.data == "clear_cart")
# async def clear_cart(callback: CallbackQuery, session: AsyncSession):
#     user_id = callback.from_user.id
#     stmt = delete(CartItem).where(CartItem.user_id == user_id)
#     await session.execute(stmt)
#     await session.commit()

#     await callback.message.answer("Корзина очищена.")
#     await callback.answer()

# @user_private_router.callback_query(F.data == "checkout")
# async def checkout(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     user_id = callback.from_user.id
#     stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
#     result = await session.execute(stmt)
#     cart_items = result.scalars().all()

#     if not cart_items:
#         await callback.message.answer("Ваша корзина пуста.")
#         await callback.answer()
#         return

#     total_price = sum(item.quantity * item.price_at_time for item in cart_items)
#     address = "Адрес самовывоза\nДеловой центр Чайка\nУлица 40 лет Победы, 50Б - офис 332"

#     # Сохраняем все товары в состояние
#     await state.update_data(
#         cart_items=[
#             {
#                 "product_id": item.product_id,
#                 "quantity": item.quantity,
#                 "total_price": item.quantity * item.price_at_time,
#                 "name": item.product.name,
#                 "price_at_time": item.price_at_time
#             } for item in cart_items
#         ],
#         total_price=total_price,
#         address=address
#     )

#     await callback.message.answer("Выберите способ получения заказа:", reply_markup=InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(text="Самовывоз", callback_data="pickup"),
#                 InlineKeyboardButton(text="Доставка", callback_data="delivery")
#             ]
#         ]
#     ))
#     await state.set_state(DeliveryState.waiting_for_pickup_datetime)
#     await callback.answer()

# @user_private_router.callback_query(F.data == "pickup")
# async def pickup_selected(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Пожалуйста, укажите дату и время самовывоза в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя самовывоза с 10:00 до 20:00.")
#     await state.set_state(DeliveryState.waiting_for_pickup_datetime)
#     await callback.answer()

# @user_private_router.callback_query(F.data == "delivery")
# async def delivery_selected(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Пожалуйста, укажите дату и время доставки в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя доставки с 10:00 до 20:00.")
#     await state.set_state(DeliveryState.waiting_for_datetime)
#     await callback.answer()

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_pickup_datetime))
# async def pickup_datetime_received(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         pickup_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return

#     current_time = datetime.datetime.now()
#     if pickup_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return

#     if not (10 <= pickup_datetime.hour < 22):
#         await message.answer("Время самовывоза должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return

#     await state.update_data(pickup_datetime=pickup_datetime)
#     await message.answer("Адрес самовывоза\nДеловой центр Чайка\nУлица 40 лет Победы, 50Б - офис 332")

#     try:
#         await bot.send_location(chat_id=message.chat.id, latitude=OFFICE_COORDS[0], longitude=OFFICE_COORDS[1])
#     except TelegramError as e:
#         print(f"Ошибка при отправке геопозиции: {e}")

#     await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
#     ]))
#     await state.set_state(DeliveryState.waiting_for_user_confirmation)

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_datetime))
# async def delivery_datetime_received(message: Message, state: FSMContext, session: AsyncSession):
#     datetime_str = message.text
#     try:
#         delivery_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
#     except ValueError:
#         await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
#         return

#     current_time = datetime.datetime.now()
#     if delivery_datetime <= current_time:
#         await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
#         return

#     if not (10 <= delivery_datetime.hour < 22):
#         await message.answer("Время доставки должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
#         return

#     if (delivery_datetime - current_time).total_seconds() < 3 * 3600:
#         await message.answer("Время доставки должно быть не менее чем через 3 часа от текущего времени. Пожалуйста, укажите корректное время.")
#         return

#     await state.update_data(delivery_datetime=delivery_datetime)
#     await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
#     ]))
#     await state.set_state(DeliveryState.waiting_for_user_confirmation)

# @user_private_router.callback_query(F.data == "payment_na_meste", StateFilter(DeliveryState.waiting_for_user_confirmation))
# async def payment_na_meste_selected(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     logging.info(f"Data from state: {data}")
#     if 'cart_items' not in data or 'total_price' not in data or 'address' not in data:
#         await callback.message.answer("Произошла ошибка: данные о заказе отсутствуют. Пожалуйста, попробуйте снова.")
#         await state.clear()
#         await callback.answer()
#         return

#     user_id = callback.from_user.id
#     cart_items = data['cart_items']
#     total_price = data['total_price']
#     address = data['address']
#     pickup_datetime = data.get('pickup_datetime')
#     delivery_datetime = data.get('delivery_datetime')
#     order_id = generate_order_id()

#     await state.update_data(order_id=order_id)

#     order_text = "Подтвердите ваш заказ:\n"
#     grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

#     for item in cart_items:
#         grouped_items[item['product_id']]["quantity"] += item['quantity']
#         grouped_items[item['product_id']]["total_price"] += item['total_price']

#     for product_id, details in grouped_items.items():
#         product = next(item for item in cart_items if item['product_id'] == product_id)
#         order_text += f"Товар: {product['name']}\n"
#         order_text += f"Количество: {details['quantity']}\n"
#         order_text += f"Общая цена: {details['total_price']} руб.\n\n"

#     order_text += f"Общая цена: {total_price} руб.\n"
#     order_text += f"Адрес: {address}\n"
#     order_text += f"Время получения: {pickup_datetime or delivery_datetime}\n"
#     order_text += f"Для подтверждения введите 'Да'."

#     await callback.message.answer(order_text)
#     await state.set_state(DeliveryState.waiting_for_user_confirmation)
#     await callback.answer()

# @user_private_router.message(StateFilter(DeliveryState.waiting_for_user_confirmation))
# async def user_confirmation_received(message: Message, state: FSMContext, session: AsyncSession):
#     if message.text.lower() == "да":
#         data = await state.get_data()
#         order_id = data['order_id']
#         user_id = message.from_user.id
#         cart_items = data['cart_items']
#         total_price = data['total_price']
#         address = data['address']
#         pickup_datetime = data.get('pickup_datetime')
#         delivery_datetime = data.get('delivery_datetime')

#         stmt = select(User).where(User.user_id == user_id)
#         result = await session.execute(stmt)
#         user = result.scalar_one_or_none()
#         referrer_id = user.referrer_id if user else None

#         grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

#         for item in cart_items:
#             grouped_items[item['product_id']]["quantity"] += item['quantity']
#             grouped_items[item['product_id']]["total_price"] += item['total_price']

#         for product_id, details in grouped_items.items():
#             product = next(item for item in cart_items if item['product_id'] == product_id)
#             name = product['name']
#             price_at_time = product['price_at_time']

#             new_order = Order(
#                 product_id=product_id,
#                 price=price_at_time,
#                 quantity=details['quantity'],
#                 name=name,
#                 maker=product.get('maker', ''),
#                 taste=data.get('taste', ''),
#                 user_id=user_id,
#                 referrer_id=referrer_id,
#                 order_number=order_id,
#                 payment_status="Не оплачен",
#                 order_status="В обработке"
#             )

#             session.add(new_order)
#             await session.commit()

#             try:
#                 await update_product_quantity(session, product_id, details['quantity'])
#             except ValueError as e:
#                 await message.answer(f"Ошибка при обновлении данных: {e}")

#         await message.answer(f"Ваш заказ (ID: {order_id}) принят. Оплата будет произведена при получении.")

#         # Формируем сообщение для админа с деталями заказа
#         msg_ad = (f"Новый заказ оплаты на месте!\n"
#                   f"Пользователь ID: {user_id}\n"
#                   f"Общая цена: {total_price} руб.\n"
#                   f"Адрес: {address}\n"
#                   f"Время получения: {pickup_datetime or delivery_datetime}\n"
#                   f"Товары:\n")

#         for product_id, details in grouped_items.items():
#             product = next(item for item in cart_items if item['product_id'] == product_id)
#             msg_ad += f"Товар: {product['name']},\n Количество: {details['quantity']},\n Общая цена: {details['total_price']} руб.\n"

#         await bot.send_message(USER_ID, msg_ad)

#         await state.clear()
#     else:
#         await message.answer("Заказ не подтвержден. Пожалуйста, введите 'Да' для подтверждения.")

# def generate_order_id():
#     timestamp = datetime.datetime.now().strftime("%Y%m%d") 
#     random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))  
#     order_id = f"ORD-{timestamp}-{random_part}"
#     return order_id









class DeliveryState(StatesGroup):
    waiting_for_pickup_datetime = State()
    waiting_for_datetime = State()
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_payment_method = State()
    waiting_for_promo_code = State()
    waiting_for_user_confirmation = State()
    waiting_for_promo_confirmation = State()  # Новое состояние для подтверждения после промокода

@user_private_router.message(F.text.lower() == "корзина 🛒")
@user_private_router.message(Command("cart"))
async def view_cart(message: types.Message, session: AsyncSession):
    user_id = message.from_user.id
    stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        await message.answer("Ваша корзина пуста.")
        return

    cart_text = "Ваша корзина:\n\n"
    total_price = 0
    grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

    for item in cart_items:
        product = item.product
        item_total_price = item.quantity * item.price_at_time
        grouped_items[product.id]["quantity"] += item.quantity
        grouped_items[product.id]["total_price"] += item_total_price
        total_price += item_total_price

    for product_id, details in grouped_items.items():
        product = next(item.product for item in cart_items if item.product.id == product_id)
        cart_text += f"{product.name} - {details['quantity']} шт. - {details['total_price']} руб.\n"

    cart_text += f"\nИтого: {total_price} руб."

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Оформить заказ", callback_data="checkout"),
                InlineKeyboardButton(text="Очистить корзину", callback_data="clear_cart"),
            ]
        ]
    )

    await message.answer(cart_text, reply_markup=keyboard)

@user_private_router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery, session: AsyncSession):
    user_id = callback.from_user.id
    stmt = delete(CartItem).where(CartItem.user_id == user_id)
    await session.execute(stmt)
    await session.commit()

    await callback.message.answer("Корзина очищена.")
    await callback.answer()

@user_private_router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_id = callback.from_user.id
    stmt = select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.user_id == user_id)
    result = await session.execute(stmt)
    cart_items = result.scalars().all()

    if not cart_items:
        await callback.message.answer("Ваша корзина пуста.")
        await callback.answer()
        return

    total_price = sum(item.quantity * item.price_at_time for item in cart_items)
    address = "Адрес самовывоза\nДеловой центр Чайка\nУлица 40 лет Победы, 50Б - офис 332"

    # Сохраняем все товары в состояние
    await state.update_data(
        cart_items=[
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "total_price": item.quantity * item.price_at_time,
                "name": item.product.name,
                "price_at_time": item.price_at_time
            } for item in cart_items
        ],
        total_price=total_price,
        address=address,
        name=cart_items[0].product.name,  # Сохраняем имя первого товара
        product_id=cart_items[0].product_id,  # Сохраняем product_id первого товара
        quantity=cart_items[0].quantity,  # Сохраняем количество первого товара
        order_id=generate_order_id()  # Генерируем и сохраняем order_id
    )

    await callback.message.answer("Выберите способ получения заказа:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Самовывоз", callback_data="pickup"),
                InlineKeyboardButton(text="Доставка", callback_data="delivery")
            ]
        ]
    ))
    await state.set_state(DeliveryState.waiting_for_pickup_datetime)
    await callback.answer()


@user_private_router.callback_query(F.data == "pickup")
async def pickup_selected(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пожалуйста, укажите дату и время самовывоза в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя самовывоза с 10:00 до 20:00.")
    await state.set_state(DeliveryState.waiting_for_pickup_datetime)
    await callback.answer()

@user_private_router.callback_query(F.data == "delivery")
async def delivery_selected(callback: CallbackQuery, state: FSMContext):
    keyboard = [
        [
            InlineKeyboardButton(text="Автозаводский", callback_data="avto"),
            InlineKeyboardButton(text="Центральный", callback_data="centr"),
        ],
        [
            InlineKeyboardButton(text="Комсомольский", callback_data="komsomol"),
            InlineKeyboardButton(text="Шлюзовой", callback_data="shlyuz")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    await callback.message.answer(text="Выберите ваш район:", reply_markup=reply_markup)
    await callback.answer()

@user_private_router.callback_query(F.data.in_(["avto", "centr", "komsomol", "shlyuz"]))
async def district_selected(callback: CallbackQuery, state: FSMContext):
    district = callback.data
    await state.update_data(district=district)
    await callback.message.answer("Пожалуйста, укажите дату и время доставки в формате ДД.ММ.ГГГГ ЧЧ:ММ.\n\nВремя доставки с 10:00 до 20:00.")
    await state.set_state(DeliveryState.waiting_for_datetime)
    await callback.answer()

@user_private_router.message(StateFilter(DeliveryState.waiting_for_pickup_datetime))
async def pickup_datetime_received(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    datetime_str = message.text
    try:
        pickup_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
        return

    current_time = datetime.datetime.now()
    if pickup_datetime <= current_time:
        await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
        return

    if not (10 <= pickup_datetime.hour < 22):
        await message.answer("Время самовывоза должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
        return

    await state.update_data(pickup_datetime=pickup_datetime)
    await message.answer("Адрес самовывоза\nДеловой центр Чайка\nУлица 40 лет Победы, 50Б - офис 332")

    try:
        await bot.send_location(chat_id=message.chat.id, latitude=OFFICE_COORDS[0], longitude=OFFICE_COORDS[1])
    except TelegramError as e:
        print(f"Ошибка при отправке геопозиции: {e}")

    await message.answer("Пожалуйста, укажите ваш номер телефона, чтобы мы могли с вами связаться.\nВ формате 89*********.")
    await state.set_state(DeliveryState.waiting_for_phone)

@user_private_router.message(StateFilter(DeliveryState.waiting_for_datetime))
async def delivery_datetime_received(message: Message, state: FSMContext, session: AsyncSession):
    datetime_str = message.text
    try:
        delivery_datetime = datetime.datetime.strptime(datetime_str, "%d.%m.%Y %H:%M")
    except ValueError:
        await message.answer("Неверный формат даты и времени. Пожалуйста, используйте формат ДД.ММ.ГГГГ ЧЧ:ММ.")
        return

    current_time = datetime.datetime.now()
    if delivery_datetime <= current_time:
        await message.answer("Указанное время уже прошло. Пожалуйста, укажите будущее время.")
        return

    if not (10 <= delivery_datetime.hour < 22):
        await message.answer("Время доставки должно быть в диапазоне с 10:00 до 20:00. Пожалуйста, укажите корректное время.")
        return

    if (delivery_datetime - current_time).total_seconds() < 3 * 3600:
        await message.answer("Время доставки должно быть не менее чем через 3 часа от текущего времени. Пожалуйста, укажите корректное время.")
        return

    await state.update_data(delivery_datetime=delivery_datetime)
    await message.answer("Пожалуйста, укажите адрес доставки.")
    await state.set_state(DeliveryState.waiting_for_address)

@user_private_router.message(StateFilter(DeliveryState.waiting_for_address))
async def address_received(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer("Пожалуйста, укажите ваш номер телефона, чтобы мы могли с вами связаться.\nВ формате 89*********.")
    await state.set_state(DeliveryState.waiting_for_phone)

@user_private_router.message(StateFilter(DeliveryState.waiting_for_phone))
async def phone_received(message: Message, state: FSMContext):
    phone = message.text
    if not re.match(r"^8\d{10}$", phone):
        await message.answer("Неверный формат номера телефона. Пожалуйста, используйте формат 89*********.")
        return

    await state.update_data(phone=phone)
    await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="При получение", callback_data="payment_na_meste")],
        [InlineKeyboardButton(text="Промокод", callback_data="payment_promo")],
    ]))
    await state.set_state(DeliveryState.waiting_for_payment_method)

@user_private_router.callback_query(F.data == "payment_na_meste", StateFilter(DeliveryState.waiting_for_payment_method))
async def payment_na_meste_selected(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    logging.info(f"Data from state: {data}")
    if 'cart_items' not in data or 'total_price' not in data or 'address' not in data or 'phone' not in data:
        await callback.message.answer("Произошла ошибка: данные о заказе отсутствуют. Пожалуйста, попробуйте снова.")
        await state.clear()
        await callback.answer()
        return

    user_id = callback.from_user.id
    cart_items = data['cart_items']
    total_price = data['total_price']
    address = data['address']
    phone = data['phone']
    pickup_datetime = data.get('pickup_datetime')
    delivery_datetime = data.get('delivery_datetime')
    district = data.get('district')
    order_id = generate_order_id()

    await state.update_data(order_id=order_id)

    order_text = "Подтвердите ваш заказ:\n"
    grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

    for item in cart_items:
        grouped_items[item['product_id']]["quantity"] += item['quantity']
        grouped_items[item['product_id']]["total_price"] += item['total_price']

    for product_id, details in grouped_items.items():
        product = next(item for item in cart_items if item['product_id'] == product_id)
        order_text += f"Товар: {product['name']}\n"
        order_text += f"Количество: {details['quantity']}\n"
        order_text += f"Общая цена: {details['total_price']} руб.\n\n"

    delivery_cost = calculate_delivery_cost(district, total_price)
    total_price_with_delivery = total_price + delivery_cost

    order_text += f"Общая цена: {total_price_with_delivery} руб.\n"
    order_text += f"Адрес: {address}\n"
    order_text += f"Телефон: {phone}\n"
    order_text += f"Время получения: {pickup_datetime or delivery_datetime}\n"
    order_text += f"Для подтверждения введите 'Да'."

    await callback.message.answer(order_text)
    await state.set_state(DeliveryState.waiting_for_user_confirmation)
    await callback.answer()

@user_private_router.message(StateFilter(DeliveryState.waiting_for_user_confirmation))
async def user_confirmation_received(message: Message, state: FSMContext, session: AsyncSession):
    if message.text.lower() == "да":
        data = await state.get_data()
        order_id = data['order_id']
        user_id = message.from_user.id
        cart_items = data['cart_items']
        total_price = data['total_price']
        address = data['address']
        phone = data['phone']
        pickup_datetime = data.get('pickup_datetime')
        delivery_datetime = data.get('delivery_datetime')
        district = data.get('district')

        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        referrer_id = user.referrer_id if user else None

        grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

        for item in cart_items:
            grouped_items[item['product_id']]["quantity"] += item['quantity']
            grouped_items[item['product_id']]["total_price"] += item['total_price']

        for product_id, details in grouped_items.items():
            product = next(item for item in cart_items if item['product_id'] == product_id)
            name = product['name']
            price_at_time = product['price_at_time']

            new_order = Order(
                product_id=product_id,
                price=price_at_time,
                quantity=details['quantity'],
                name=name,
                maker=product.get('maker', ''),
                taste=data.get('taste', ''),
                user_id=user_id,
                referrer_id=referrer_id,
                order_number=order_id,
                payment_status="Не оплачен",
                order_status="В обработке"
            )

            session.add(new_order)
            await session.commit()

            # try:
            #     await update_product_quantity(session, product_id, details['quantity'])
            # except ValueError as e:
            #     await message.answer(f"Ошибка при обновлении данных: {e}")

        await message.answer(f"Ваш заказ (ID: {order_id}) принят. Оплата будет произведена при получении.")

        # Рассчитываем стоимость доставки
        delivery_cost = calculate_delivery_cost(district, total_price)
        total_price_with_delivery = total_price + delivery_cost

        # Формируем сообщение для админа с деталями заказа
        msg_ad = (f"Новый заказ оплаты на месте!\n"
                  f"Пользователь ID: {user_id}\n"
                  f"Общая цена: {total_price} руб.\n"
                  f"Стоимость доставки: {delivery_cost} руб.\n"
                  f"Итоговая цена с доставкой: {total_price_with_delivery} руб.\n"
                  f"Адрес: {address}\n"
                  f"Телефон: {phone}\n"
                  f"Время получения: {pickup_datetime or delivery_datetime}\n"
                  f"Товары:\n")

        for product_id, details in grouped_items.items():
            product = next(item for item in cart_items if item['product_id'] == product_id)
            msg_ad += f"Товар: {product['name']},\n Количество: {details['quantity']},\n Общая цена: {details['total_price']} руб.\n"

        await bot.send_message(USER_ID, msg_ad)
        stmt = delete(CartItem).where(CartItem.user_id == user_id)
        await session.execute(stmt)
        await session.commit()


        await state.clear()
    else:
        await message.answer("Заказ не подтвержден. Пожалуйста, введите 'Да' для подтверждения.")

@user_private_router.callback_query(F.data == "payment_promo", StateFilter(DeliveryState.waiting_for_payment_method))
async def payment_promo_selected(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите промокод:")
    await state.set_state(DeliveryState.waiting_for_promo_code)
    await callback.answer()

@user_private_router.message(StateFilter(DeliveryState.waiting_for_promo_code))
async def promo_code_received(message: Message, state: FSMContext, session: AsyncSession):
    promo_code = message.text
    data = await state.get_data()
    total_price = float(data['total_price'])  # Преобразуем в float
    name = data.get('name')  # Используем get для безопасного доступа
    address = data['address']
    pickup_datetime = data.get('pickup_datetime')
    delivery_datetime = data.get('delivery_datetime')
    product_id = data.get('product_id')  # Получаем product_id
    quantity = data.get('quantity')  # Получаем количество

    success, new_total_price = await activate_promo_code(session, promo_code, total_price)
    if success:
        await message.answer(f"Промокод применен. Новая сумма: {new_total_price} руб.")
    else:
        await message.answer("Промокод не найден.")

    method = "С" if pickup_datetime else "Д"
    datetime_str = pickup_datetime.strftime('%d%m%Y%H%M') if pickup_datetime else delivery_datetime.strftime('%d%m%Y%H%M')
    payload = f"{method}_{product_id}_{quantity}_{new_total_price}_{name}_{address}_{datetime_str}_{promo_code}"

    await state.update_data(total_price=new_total_price, payload=payload)

    # Запрашиваем подтверждение заказа
    order_text = "Подтвердите ваш заказ:\n"
    grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

    for item in data['cart_items']:
        grouped_items[item['product_id']]["quantity"] += item['quantity']
        grouped_items[item['product_id']]["total_price"] += item['total_price']

    for product_id, details in grouped_items.items():
        product = next(item for item in data['cart_items'] if item['product_id'] == product_id)
        order_text += f"Товар: {product['name']}\n"
        order_text += f"Количество: {details['quantity']}\n"
        order_text += f"Общая цена: {details['total_price']} руб.\n\n"

    delivery_cost = calculate_delivery_cost(data.get('district'), new_total_price)
    total_price_with_delivery = new_total_price + delivery_cost

    order_text += f"Общая цена: {total_price_with_delivery} руб.\n"
    order_text += f"Адрес: {address}\n"
    order_text += f"Телефон: {data['phone']}\n"
    order_text += f"Время получения: {pickup_datetime or delivery_datetime}\n"
    order_text += f"Для подтверждения введите 'Да'."

    await message.answer(order_text)
    await state.set_state(DeliveryState.waiting_for_promo_confirmation)


@user_private_router.message(StateFilter(DeliveryState.waiting_for_promo_confirmation))
async def promo_confirmation_received(message: Message, state: FSMContext, session: AsyncSession):
    if message.text.lower() == "да":
        data = await state.get_data()
        order_id = data.get('order_id')  # Используем get для безопасного доступа
        if not order_id:
            await message.answer("Произошла ошибка: идентификатор заказа отсутствует. Пожалуйста, попробуйте снова.")
            await state.clear()
            return

        user_id = message.from_user.id
        cart_items = data['cart_items']
        total_price = data['total_price']
        address = data['address']
        phone = data['phone']
        pickup_datetime = data.get('pickup_datetime')
        delivery_datetime = data.get('delivery_datetime')
        district = data.get('district')

        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        referrer_id = user.referrer_id if user else None

        grouped_items = defaultdict(lambda: {"quantity": 0, "total_price": 0})

        for item in cart_items:
            grouped_items[item['product_id']]["quantity"] += item['quantity']
            grouped_items[item['product_id']]["total_price"] += item['total_price']

        for product_id, details in grouped_items.items():
            product = next(item for item in cart_items if item['product_id'] == product_id)
            name = product['name']
            price_at_time = product['price_at_time']

            new_order = Order(
                product_id=product_id,
                price=price_at_time,
                quantity=details['quantity'],
                name=name,
                maker=product.get('maker', ''),
                taste=data.get('taste', ''),
                user_id=user_id,
                referrer_id=referrer_id,
                order_number=order_id,
                payment_status="Не оплачен",
                order_status="В обработке"
            )

            session.add(new_order)
            await session.commit()

        await message.answer(f"Ваш заказ (ID: {order_id}) принят. Оплата будет произведена при получении.")

        delivery_cost = calculate_delivery_cost(district, total_price)
        total_price_with_delivery = total_price + delivery_cost

        msg_ad = (f"Новый заказ оплаты на месте!\n"
                  f"Пользователь ID: {user_id}\n"
                  f"Общая цена: {total_price} руб.\n"
                  f"Стоимость доставки: {delivery_cost} руб.\n"
                  f"Итоговая цена с доставкой: {total_price_with_delivery} руб.\n"
                  f"Адрес: {address}\n"
                  f"Телефон: {phone}\n"
                  f"Время получения: {pickup_datetime or delivery_datetime}\n"
                  f"Товары:\n")

        for product_id, details in grouped_items.items():
            product = next(item for item in cart_items if item['product_id'] == product_id)
            msg_ad += f"Товар: {product['name']},\n Количество: {details['quantity']},\n Общая цена: {details['total_price']} руб.\n"

        await bot.send_message(USER_ID, msg_ad)
        stmt = delete(CartItem).where(CartItem.user_id == user_id)
        await session.execute(stmt)
        await session.commit()


        await state.clear()
    else:
        await message.answer("Заказ не подтвержден. Пожалуйста, введите 'Да' для подтверждения.")


async def activate_promo_code(session: AsyncSession, promo_code: str, total_price: int) -> tuple[bool, int]:
    stmt = select(Promocode).filter(Promocode.name == promo_code)
    result = await session.execute(stmt)
    promo = result.scalar_one_or_none()

    if promo:
        discount_amount_float = float(promo.discount_amount)  # Преобразуем в float
        if promo.discount_type == 'PERCENT':
            discount = total_price * (discount_amount_float / 100)
        else:
            discount = discount_amount_float
        total_price -= discount
        await delete_promo_code(session, promo_code)
        return True, total_price
    else:
        return False, total_price
    

async def delete_promo_code(session: AsyncSession, promo_code: str):
    stmt = delete(Promocode).where(Promocode.name == promo_code)
    await session.execute(stmt)
    await session.commit()

def calculate_delivery_cost(district, total_price):
    delivery_cost = 0

    if district == "avto":
        if total_price < 1000:
            delivery_cost = 50
    elif district == "centr":
        if total_price < 2000:
            delivery_cost = 100
    elif district == "komsomol":
        if total_price < 3000:
            delivery_cost = 150
    elif district == "shlyuz":
        if total_price < 4000:
            delivery_cost = 200

    return delivery_cost

def generate_order_id():
    timestamp = datetime.datetime.now().strftime("%Y%m%d") 
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))  
    order_id = f"ORD-{timestamp}-{random_part}"
    return order_id

