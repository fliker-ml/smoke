from aiogram import F, Router, types, Bot
from aiogram.filters import Command, StateFilter, or_f


from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.models import Promocode, User, Order
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.orm_query import (
    orm_get_categories,
    orm_add_product,
    orm_delete_product,
    orm_get_product,
    orm_get_products,
    orm_update_product,
    orm_get_makers_by_category,
    orm_get_products_by_maker,
    get_products_with_tastes,
    get_user_balance,
    update_user_balance,
    get_products_with_tastes_admin

)
from filters.chat_types import ChatTypeFilter, IsAdmin
from kbds.inline import get_callback_btns
from kbds.reply import get_keyboard
from sqlalchemy.exc import IntegrityError
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from datetime import datetime
from database.models import  Product, Promocode, Order, User, Favourite, Category, CartItem

from aiogram.utils.keyboard import InlineKeyboardBuilder

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())
promokod = []





ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Управление заказами",
    "Управление промокодами",
    "Управление балансом",
    placeholder="Выберите действие",
    sizes=(2,1,2),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


def get_callback_btns2(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


@admin_router.message(F.text == 'Ассортимент', IsAdmin())
async def admin_category(message: types.Message, session: AsyncSession):
    categories = await orm_get_categories(session=session)  # Замените на ваш ORM-запрос для получения категорий
    btns = {category.name: f"admin_maker_{category.id}" for category in categories}
    await message.answer("Выберите категорию:", reply_markup=get_callback_btns2(btns=btns))


@admin_router.callback_query(F.data.startswith("admin_maker_"), IsAdmin())
async def admin_maker(callback: CallbackQuery, session: AsyncSession):
    category_id = int(callback.data.split("_")[2])  # Извлекаем ID категории из callback data
    products = await orm_get_makers_by_category(category_id=category_id, session=session)
    btns = {product.maker: f"admin_product_{product.maker}" for product in products}
    await callback.message.edit_text(f"Производители в категории:", reply_markup=get_callback_btns2(btns=btns))
@admin_router.callback_query(F.data.startswith("admin_product_"), IsAdmin())

async def admin_products(callback: CallbackQuery, session: AsyncSession):
    maker = callback.data.split("_")[2]
    products = await get_products_with_tastes_admin(maker=maker, session=session)
    if not products:
        await callback.message.answer(f"Нет продуктов производителя {maker}.")
        return

    btns = {product[1]: f"product_{product[0]}_{product[2]}" for product in products}  # Include category_id in the callback data
    await callback.message.edit_text(f"Вкусы производителя:", reply_markup=get_callback_btns2(btns=btns))

@admin_router.callback_query(F.data.startswith("admin_product_"), IsAdmin())
async def admin_products(callback: CallbackQuery, session: AsyncSession):
    maker = callback.data.split("_")[2]
    products = await get_products_with_tastes_admin(maker=maker, session=session)
    if not products:
        await callback.message.answer(f"Нет продуктов производителя {maker}.")
        return

    btns = {f"{product.name} ({product.taste})": f"product_{product.id}" for product in products}
    await callback.message.edit_text(f"Вкусы производителя:", reply_markup=get_callback_btns2(btns=btns))


@admin_router.callback_query(F.data.startswith("product_"), IsAdmin())
async def product_details(callback: CallbackQuery, session: AsyncSession):
    product_id = int(callback.data.split("_")[1])  
    product = await orm_get_product(session=session, product_id=product_id)
    if product:
        status = "Скрыт" if product.is_closed else "Открыт"
        if product.image:
            await callback.message.answer_photo(
                photo=product.image,
                caption=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅Количество товара: {product.quantity}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}\n<strong>🔒 Статус:</strong> {status}",
                reply_markup=get_callback_btns2(
                    btns={
                        "Удалить": f"delete_{product.id}",
                        "Изменить": f"change_{product.id}",
                    },
                    sizes=(2,)
                ),
            )
        else:
            await callback.message.answer(
                text=f"<strong>📦 Товар:</strong> {product.name}\n<strong>😋 Вкус:</strong> {product.taste}\n<strong>📃 Описание:</strong> {product.description}\n\n<strong>✅Количество товара: {product.quantity}</strong>\n<strong>💰 Стоимость:</strong> {round(product.price, 2)}\n<strong>🔒 Статус:</strong> {status}",
                reply_markup=get_callback_btns2(
                    btns={
                        "Удалить": f"delete_{product.id}",
                        "Изменить": f"change_{product.id}",
                    },
                    sizes=(2,)
                ),
                parse_mode="HTML"
            )
    await callback.answer()


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))
    await callback.answer("Товар удален")
    await callback.message.answer("Товар удален!")


# class AddProduct(StatesGroup):
#     name = State()
#     description = State()
#     category = State()
#     price = State()
#     image = State()
#     maker = State()
#     quantity = State()
#     taste = State()

#     product_for_change = None

#     texts = {
#         "AddProduct:name": "Введите название заново:",
#         "AddProduct:description": "Введите описание заново:",
#         "AddProduct:category": "Выберите категорию  заново ⬆️",
#         "AddProduct:price": "Введите стоимость заново:",
#         "AddProduct:image": "Этот стейт последний, поэтому...",
#         "AddProduct:maker": "Введите производителя заново:",
#         "AddProduct:quantity": "Введите количество заново:",
#         "AddProduct:taste": "Введите вкус заново:",
#     }


# # Становимся в состояние ожидания ввода name
# @admin_router.message(StateFilter(None), F.text == "Добавить товар")
# async def add_product(message: types.Message, state: FSMContext):
#     await message.answer(
#         "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
#     )
#     await state.set_state(AddProduct.name)

# # Ловим данные для состояние name и потом меняем состояние на description
# @admin_router.message(AddProduct.name, F.text)
# async def add_name(message: types.Message, state: FSMContext):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(name=AddProduct.product_for_change.name)
#     else:
#         await state.update_data(name=message.text)
#     await message.answer("Введите описание товара")
#     await state.set_state(AddProduct.description)

# # Ловим данные для состояние description и потом меняем состояние на category
# @admin_router.message(AddProduct.description, F.text)
# async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(description=AddProduct.product_for_change.description)
#     else:
#         await state.update_data(description=message.text)

#     categories = await orm_get_categories(session)
#     btns = {category.name : str(category.id) for category in categories}
#     await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
#     await state.set_state(AddProduct.category)

# # Ловим callback выбора категории
# @admin_router.callback_query(AddProduct.category)
# async def category_choice(callback: types.CallbackQuery, state: FSMContext , session: AsyncSession):
#     if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
#         await callback.answer()
#         await state.update_data(category=callback.data)
#         await callback.message.answer('Теперь введите цену товара.')
#         await state.set_state(AddProduct.price)
#     else:
#         await callback.message.answer('Выберите катеорию из кнопок.')
#         await callback.answer()

# # Ловим данные для состояние price и потом меняем состояние на image
# @admin_router.message(AddProduct.price, F.text)
# async def add_price(message: types.Message, state: FSMContext):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(price=AddProduct.product_for_change.price)
#     else:
#         try:
#             float(message.text)
#         except ValueError:
#             await message.answer("Введите корректное значение цены")
#             return

#         await state.update_data(price=message.text)
#     await message.answer("Загрузите изображение товара")
#     await state.set_state(AddProduct.image)

# # Ловим данные для состояние image и потом меняем состояние на maker
# @admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
# async def add_image(message: types.Message, state: FSMContext):
#     if message.text and message.text == "." and AddProduct.product_for_change:
#         await state.update_data(image=AddProduct.product_for_change.image)
#     elif message.photo:
#         await state.update_data(image=message.photo[-1].file_id)
#     else:
#         await message.answer("Отправьте фото товара")
#         return
#     await message.answer("Введите производителя товара")
#     await state.set_state(AddProduct.maker)

# # Ловим данные для состояние maker и потом меняем состояние на quantity
# @admin_router.message(AddProduct.maker, F.text)
# async def add_maker(message: types.Message, state: FSMContext):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(maker=AddProduct.product_for_change.maker)
#     else:
#         await state.update_data(maker=message.text)
#     await message.answer("Введите количество товара")
#     await state.set_state(AddProduct.quantity)

# # Ловим данные для состояние quantity и потом меняем состояние на taste
# @admin_router.message(AddProduct.quantity, F.text)
# async def add_quantity(message: types.Message, state: FSMContext):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(quantity=AddProduct.product_for_change.quantity)
#     else:
#         try:
#             int(message.text)
#         except ValueError:
#             await message.answer("Введите корректное значение количества")
#             return

#         await state.update_data(quantity=message.text)
#     await message.answer("Введите вкус товара")
#     await state.set_state(AddProduct.taste)

# # Ловим данные для состояние taste и потом выходим из состояний
# @admin_router.message(AddProduct.taste, F.text)
# async def add_taste(message: types.Message, state: FSMContext, session: AsyncSession):
#     if message.text == "." and AddProduct.product_for_change:
#         await state.update_data(taste=AddProduct.product_for_change.taste)
#     else:
#         await state.update_data(taste=message.text)

#     data = await state.get_data()
#     try:
#         if AddProduct.product_for_change:
#             await orm_update_product(session, AddProduct.product_for_change.id, data)
#         else:
#             await orm_add_product(session, data)
#         await message.answer("Товар добавлен/изменен", reply_markup=ADMIN_KB)
#         await state.clear()

#     except Exception as e:
#         await message.answer(
#             f"Ошибка: \n{str(e)}\nОбратись к программу")
class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()
    maker = State()
    quantity = State()
    taste = State()
    is_closed = State()  # Добавляем новое состояние для выбора статуса товара

    product_for_change = None

    texts = {
        "AddProduct:name": "Введите название заново:",
        "AddProduct:description": "Введите описание заново:",
        "AddProduct:category": "Выберите категорию  заново ⬆️",
        "AddProduct:price": "Введите стоимость заново:",
        "AddProduct:image": "Этот стейт последний, поэтому...",
        "AddProduct:maker": "Введите производителя заново:",
        "AddProduct:quantity": "Введите количество заново:",
        "AddProduct:taste": "Введите вкус заново:",
    }

# Становимся в состояние ожидания ввода name
@admin_router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: types.Message, state: FSMContext):
    await message.answer(
        "Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)

# Ловим данные для состояние name и потом меняем состояние на description
@admin_router.message(AddProduct.name, F.text)
async def add_name(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(name=AddProduct.product_for_change.name)
    else:
        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)

# Ловим данные для состояние description и потом меняем состояние на category
@admin_router.message(AddProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    btns = {category.name : str(category.id) for category in categories}
    await message.answer("Выберите категорию", reply_markup=get_callback_btns(btns=btns))
    await state.set_state(AddProduct.category)

# Ловим callback выбора категории
@admin_router.callback_query(AddProduct.category)
async def category_choice(callback: types.CallbackQuery, state: FSMContext , session: AsyncSession):
    if int(callback.data) in [category.id for category in await orm_get_categories(session)]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer('Теперь введите цену товара.')
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer('Выберите катеорию из кнопок.')
        await callback.answer()

# Ловим данные для состояние price и потом меняем состояние на image
@admin_router.message(AddProduct.price, F.text)
async def add_price(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("Введите корректное значение цены")
            return

        await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)

# Ловим данные для состояние image и потом меняем состояние на maker
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == "."))
async def add_image(message: types.Message, state: FSMContext):
    if message.text and message.text == "." and AddProduct.product_for_change:
        await state.update_data(image=AddProduct.product_for_change.image)
    elif message.photo:
        await state.update_data(image=message.photo[-1].file_id)
    else:
        await message.answer("Отправьте фото товара")
        return
    await message.answer("Введите производителя товара")
    await state.set_state(AddProduct.maker)

# Ловим данные для состояние maker и потом меняем состояние на quantity
@admin_router.message(AddProduct.maker, F.text)
async def add_maker(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(maker=AddProduct.product_for_change.maker)
    else:
        await state.update_data(maker=message.text)
    await message.answer("Введите количество товара")
    await state.set_state(AddProduct.quantity)

# Ловим данные для состояние quantity и потом меняем состояние на taste
@admin_router.message(AddProduct.quantity, F.text)
async def add_quantity(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(quantity=AddProduct.product_for_change.quantity)
    else:
        try:
            int(message.text)
        except ValueError:
            await message.answer("Введите корректное значение количества")
            return

        await state.update_data(quantity=message.text)
    await message.answer("Введите вкус товара")
    await state.set_state(AddProduct.taste)

# Ловим данные для состояние taste и потом меняем состояние на is_closed
@admin_router.message(AddProduct.taste, F.text)
async def add_taste(message: types.Message, state: FSMContext):
    if message.text == "." and AddProduct.product_for_change:
        await state.update_data(taste=AddProduct.product_for_change.taste)
    else:
        await state.update_data(taste=message.text)

    await message.answer("Товар будет:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Скрыт", callback_data="is_closed_true")],
            [InlineKeyboardButton(text="Открыт", callback_data="is_closed_false")]
        ]
    ))
    await state.set_state(AddProduct.is_closed)

# Ловим callback выбора статуса товара и добавляем/изменяем товар в базе данных
@admin_router.callback_query(AddProduct.is_closed)
async def add_is_closed(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    is_closed = callback.data == "is_closed_true"
    await state.update_data(is_closed=is_closed)

    data = await state.get_data()
    try:
        if AddProduct.product_for_change:
            await orm_update_product(session, AddProduct.product_for_change.id, data)
        else:
            await orm_add_product(session, data)
        await callback.message.answer("Товар добавлен/изменен", reply_markup=ADMIN_KB)
        await state.clear()
    except Exception as e:
        await callback.message.answer(
            f"Ошибка: \n{str(e)}\nОбратись к программисту")
    await callback.answer()


























# class PromocodeManagement(StatesGroup):
#     waiting_for_name = State()
#     waiting_for_value = State()
#     waiting_for_type = State()
#     waiting_for_user_id = State()

# @admin_router.message(F.text == 'Управление промокодами')
# async def manage_promocodes(message: types.Message, state: FSMContext):
#     await message.answer("Выберите действие:", reply_markup=InlineKeyboardMarkup(
#         inline_keyboard=[
#             [InlineKeyboardButton(text="Создать промокод", callback_data="create_promocode")],
#             [InlineKeyboardButton(text="Просмотреть все промокоды", callback_data="view_promocodes")]
#         ]
#     ))

# @admin_router.callback_query(F.data == 'create_promocode')
# async def create_promocode(callback: CallbackQuery, state: FSMContext):
#     await callback.message.answer("Введите название промокода:")
#     await state.set_state(PromocodeManagement.waiting_for_name)
#     await callback.answer()

# @admin_router.message(PromocodeManagement.waiting_for_name)
# async def promocode_name_entered(message: types.Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await message.answer("Введите значение промокода:")
#     await state.set_state(PromocodeManagement.waiting_for_value)

# @admin_router.message(PromocodeManagement.waiting_for_value)
# async def promocode_value_entered(message: types.Message, state: FSMContext):
#     try:
#         value = float(message.text)
#         await state.update_data(value=value)
#         await message.answer("Выберите тип промокода:", reply_markup=InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="Рубли", callback_data="RUB")],
#                 [InlineKeyboardButton(text="Проценты", callback_data="PERCENT")]
#             ]
#         ))
#         await state.set_state(PromocodeManagement.waiting_for_type)
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректное значение.")

# @admin_router.callback_query(PromocodeManagement.waiting_for_type)
# async def promocode_type_selected(callback: CallbackQuery, state: FSMContext):
#     if callback.data == "PERCENT" and (await state.get_data()).get('value') > 100:
#         await callback.message.answer("Процент не может быть больше 100.")
#         await state.set_state(PromocodeManagement.waiting_for_value)
#     else:
#         await state.update_data(type=callback.data)
#         await callback.message.answer("Введите ID пользователя, к которому привязать промокод (или 0, если не нужно):")
#         await state.set_state(PromocodeManagement.waiting_for_user_id)
#     await callback.answer()

# @admin_router.message(PromocodeManagement.waiting_for_user_id)
# async def promocode_user_id_entered(message: types.Message, state: FSMContext, session: AsyncSession):
#     try:
#         user_id = int(message.text)
#         if user_id != 0:
#             # Проверяем существование пользователя по user_id и получаем его id
#             user = await session.execute(select(User).where(User.user_id == user_id))
#             user = user.scalar()
#             if not user:
#                 await message.answer(f"Пользователь с ID {user_id} не найден. Введите другой ID или 0, чтобы не привязывать промокод к пользователю.")
#                 return
#             user_id = user.id  # Используем id пользователя из таблицы user
#         data = await state.get_data()
#         await session.execute(insert(Promocode).values(
#             name=data['name'],
#             discount_amount=data['value'],
#             discount_type=data['type'],
#             user_id=user_id if user_id != 0 else None
#         ))
#         await session.commit()
#         await message.answer("Промокод успешно создан.")
#         await state.clear()
#     except ValueError:
#         await message.answer("Пожалуйста, введите корректный ID пользователя.")
#     except IntegrityError as e:
#         await session.rollback()
#         await message.answer("Произошла ошибка при создании промокода. Пожалуйста, попробуйте снова.")
class PromocodeManagement(StatesGroup):
    waiting_for_name = State()
    waiting_for_value = State()
    waiting_for_type = State()
    waiting_for_user_id = State()

@admin_router.message(F.text == 'Управление промокодами')
async def manage_promocodes(message: types.Message, state: FSMContext):
    await message.answer("Выберите действие:", reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать промокод", callback_data="create_promocode")],
            [InlineKeyboardButton(text="Просмотреть все промокоды", callback_data="view_promocodes")]
        ]
    ))

@admin_router.callback_query(F.data == 'create_promocode')
async def create_promocode(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название промокода:")
    await state.set_state(PromocodeManagement.waiting_for_name)
    await callback.answer()

@admin_router.message(PromocodeManagement.waiting_for_name)
async def promocode_name_entered(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите значение промокода:")
    await state.set_state(PromocodeManagement.waiting_for_value)

@admin_router.message(PromocodeManagement.waiting_for_value)
async def promocode_value_entered(message: types.Message, state: FSMContext):
    try:
        value = float(message.text)
        await state.update_data(value=value)
        await message.answer("Выберите тип промокода:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Рубли", callback_data="RUB")],
                [InlineKeyboardButton(text="Проценты", callback_data="PERCENT")]
            ]
        ))
        await state.set_state(PromocodeManagement.waiting_for_type)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное значение.")

@admin_router.callback_query(PromocodeManagement.waiting_for_type)
async def promocode_type_selected(callback: CallbackQuery, state: FSMContext):
    if callback.data == "PERCENT" and (await state.get_data()).get('value') > 100:
        await callback.message.answer("Процент не может быть больше 100.")
        await state.set_state(PromocodeManagement.waiting_for_value)
    else:
        await state.update_data(type=callback.data)
        await callback.message.answer("Введите ID пользователя, к которому привязать промокод (или 0, если не нужно):")
        await state.set_state(PromocodeManagement.waiting_for_user_id)
    await callback.answer()

@admin_router.message(PromocodeManagement.waiting_for_user_id)
async def promocode_user_id_entered(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        user_id = int(message.text)
        if user_id != 0:
            # Проверяем существование пользователя по user_id и получаем его id
            user = await session.execute(select(User).where(User.user_id == user_id))
            user = user.scalar()
            if not user:
                await message.answer(f"Пользователь с ID {user_id} не найден. Введите другой ID или 0, чтобы не привязывать промокод к пользователю.")
                return
            user_id = user.id  # Используем id пользователя из таблицы user
        data = await state.get_data()
        await session.execute(insert(Promocode).values(
            name=data['name'],
            discount_amount=data['value'],
            discount_type=data['type'],
            user_id=user_id if user_id != 0 else None
        ))
        await session.commit()
        await message.answer("Промокод успешно создан.")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя.")
    except IntegrityError as e:
        await session.rollback()
        await message.answer("Произошла ошибка при создании промокода. Пожалуйста, попробуйте снова.")

@admin_router.callback_query(F.data == 'view_promocodes')
async def view_promocodes(callback: CallbackQuery, session: AsyncSession):
    stmt = select(Promocode).options(joinedload(Promocode.user))
    result = await session.execute(stmt)
    promocodes = result.scalars().unique().all()

    if not promocodes:
        await callback.message.answer("Нет доступных промокодов.")
        await callback.answer()
        return

    for promocode in promocodes:
        user_id = promocode.user.user_id if promocode.user else "Не привязан"
        promocode_message = (
            f"Промокод: {promocode.name}\n"
            f"Значение: {promocode.discount_amount} {promocode.discount_type}\n"
            f"Привязан к пользователю: {user_id}"
        )
        await callback.message.answer(promocode_message)

    await callback.answer()




class BalanceManagement(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_action = State()
    waiting_for_amount = State()

@admin_router.message(F.text == 'Управление балансом', IsAdmin())
async def manage_balance(message: types.Message, state: FSMContext):
    await message.answer("Введите ID пользователя, баланс которого вы хотите управлять:")
    await state.set_state(BalanceManagement.waiting_for_user_id)

@admin_router.message(BalanceManagement.waiting_for_user_id)
async def user_id_entered(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        await state.update_data(user_id=user_id)
        await message.answer("Выберите действие:", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Начислить баланс", callback_data="add_balance")],
                [InlineKeyboardButton(text="Отнять баланс", callback_data="subtract_balance")],
                [InlineKeyboardButton(text="Просмотреть баланс", callback_data="view_balance")]
            ]
        ))
        await state.set_state(BalanceManagement.waiting_for_action)
    except ValueError:
        await message.answer("Пожалуйста, введите корректный ID пользователя.")

@admin_router.callback_query(BalanceManagement.waiting_for_action)
async def action_selected(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    action = callback.data
    await state.update_data(action=action)
    if action == "view_balance":
        data = await state.get_data()
        user_id = data.get('user_id')
        balance = await get_user_balance(session, user_id)
        await callback.message.answer(f"Баланс пользователя {user_id}: {balance}")
        await state.clear()
    else:
        await callback.message.answer("Введите сумму:")
        await state.set_state(BalanceManagement.waiting_for_amount)
    await callback.answer()

@admin_router.message(BalanceManagement.waiting_for_amount)
async def amount_entered(message: types.Message, state: FSMContext, session: AsyncSession):
    try:
        amount = int(message.text)
        data = await state.get_data()
        user_id = data.get('user_id')
        action = data.get('action')
        if action == "add_balance":
            await update_user_balance(session, user_id, amount)
            await message.answer(f"Баланс пользователя {user_id} начислен на сумму {amount}.")
        elif action == "subtract_balance":
            await update_user_balance(session, user_id, -amount)
            await message.answer(f"С баланса пользователя {user_id} снята сумма {amount}.")
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")

async def get_user_balance(session: AsyncSession, user_id: int) -> int:
    stmt = select(User.balance).where(User.user_id == user_id)
    result = await session.execute(stmt)
    balance = result.scalar()
    return balance or 0

async def update_user_balance(session: AsyncSession, user_id: int, amount: int):
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar()
    if user:
        user.balance += amount
        await session.commit()
    else:
        await session.rollback()
        raise ValueError(f"Пользователь с ID {user_id} не найден.")











class OrderManagement(StatesGroup):
    viewing_orders = State()
    changing_order_status = State()

@admin_router.message(F.text == 'Управление заказами', IsAdmin())
async def manage_orders(message: types.Message, state: FSMContext, session: AsyncSession):
    await message.answer("Просмотр всех заказов:")
    await state.set_state(OrderManagement.viewing_orders)
    await show_all_orders(message, state, session)

async def show_all_orders(message: types.Message, state: FSMContext, session: AsyncSession):
    stmt = (
        select(Order)
        .options(joinedload(Order.product))
        .where(Order.order_status != 'Выдан')
        .order_by(Order.id)
    )
    result = await session.execute(stmt)
    orders = result.scalars().unique().all()

    if not orders:
        await message.answer("Нет доступных заказов.")
        return

    for order in orders:
        product = order.product
        created_time = datetime.fromisoformat(str(order.created)).strftime('%Y-%m-%d %H:%M:%S')
        order_message = (
            f"Заказ: {order.order_number}\n"
            f"Пользователь: {order.user_id}\n"
            f"Название: {product.name}, Производитель: {product.maker}, Вкус: {product.taste}\n"
            f"Цена: {order.price}\n"
            f"Количество: {order.quantity}\n"
            f"Payment Status: {order.payment_status}\n"
            f"Order Status: {order.order_status}\n"
            f"Время создания: {created_time}"
        )
        await message.answer(order_message, reply_markup=get_order_status_keyboard(order.id))

def get_order_status_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Принять", callback_data=f"status_accept_{order_id}")],
            [InlineKeyboardButton(text="Отменить", callback_data=f"status_cancel_{order_id}")],  # Новая кнопка
            [InlineKeyboardButton(text="Готов к выдаче", callback_data=f"status_ready_{order_id}")],
            [InlineKeyboardButton(text="В доставке", callback_data=f"status_delivery_{order_id}")],
            [InlineKeyboardButton(text="Выдан", callback_data=f"status_delivered_{order_id}")]
        ]
    )


@admin_router.callback_query(F.data.startswith('status_'))
async def status_selected(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = callback.data.split('_')
    new_status = data[1]
    order_id = int('_'.join(data[2:])) 

    status_mapping = {
        "accept": "Принят",
        "cancel": "Отменен",  # Новый статус
        "ready": "Готов к выдаче",
        "delivery": "В доставке",
        "delivered": "Выдан"
    }
    new_status_ru = status_mapping.get(new_status, new_status)

    # Получаем информацию о заказе
    order_stmt = select(Order).where(Order.id == order_id)
    order_result = await session.execute(order_stmt)
    order = order_result.scalars().one()

    if new_status == "accept":
        # Списываем количество товаров
        product_stmt = update(Product).where(Product.id == order.product_id).values(
            quantity=Product.quantity - order.quantity
        )
        await session.execute(product_stmt)
    elif new_status == "cancel":
        # Возвращаем количество товаров
        product_stmt = update(Product).where(Product.id == order.product_id).values(
            quantity=Product.quantity + order.quantity
        )
        await session.execute(product_stmt)

    # Обновляем статус заказа
    order_stmt = update(Order).where(Order.id == order_id).values(order_status=new_status_ru)
    await session.execute(order_stmt)
    await session.commit()

    if new_status == "delivered":
        await mark_order_as_delivered(order_id, session)

    await callback.message.answer(f"Статус заказа {order_id} изменен на {new_status_ru}.")
    await callback.answer()

async def cancel_order(session: AsyncSession, order_id: int):
    # Получаем информацию о заказе
    order_stmt = select(Order).where(Order.id == order_id)
    order_result = await session.execute(order_stmt)
    order = order_result.scalars().one()

    # Возвращаем количество товаров
    product_stmt = update(Product).where(Product.id == order.product_id).values(
        quantity=Product.quantity + order.quantity
    )
    await session.execute(product_stmt)

    # Удаляем заказ
    delete_stmt = delete(Order).where(Order.id == order_id)
    await session.execute(delete_stmt)
    await session.commit()
# @admin_router.callback_query(F.data.startswith('status_'))
# async def status_selected(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
#     data = callback.data.split('_')
#     new_status = data[1]
#     order_id = int('_'.join(data[2:])) 

#     status_mapping = {
#         "accept": "Принят",
#         "cancel": "Отменен",  # Новый статус
#         "ready": "Готов к выдаче",
#         "delivery": "В доставке",
#         "delivered": "Выдан"
#     }
#     new_status_ru = status_mapping.get(new_status, new_status)

#     if new_status == "cancel":
#         await cancel_order(session, order_id)
#     else:
#         stmt = update(Order).where(Order.id == order_id).values(order_status=new_status_ru)
#         await session.execute(stmt)
#         await session.commit()

#         if new_status == "delivered":
#             await mark_order_as_delivered(order_id, session)

#     await callback.message.answer(f"Статус заказа {order_id} изменен на {new_status_ru}.")
#     await callback.answer()

# async def cancel_order(session: AsyncSession, order_id: int):
#     stmt = delete(Order).where(Order.id == order_id)
#     await session.execute(stmt)
#     await session.commit()


async def mark_order_as_delivered(order_id: int, session: AsyncSession):
    # Обновление статуса заказа на "Выдан" и статуса оплаты на "Оплачено"
    await session.execute(
        update(Order).
        where(Order.id == order_id).
        values(order_status='Выдан', payment_status='Оплачено')
    )

    # Получение информации о заказе
    result = await session.execute(
        select(Order).
        where(Order.id == order_id)
    )
    order = result.scalars().one()

    # Расчет общей суммы заказа
    total_amount = float(order.price) * order.quantity

    # Начисление баллов пользователю
    user_update = update(User).where(User.user_id == order.user_id).values(
        balance=User.balance + int(total_amount * 0.1),
        spent=User.spent + total_amount
    )
    await session.execute(user_update)

    # Начисление баллов рефереру, если он есть
    if order.referrer_id:
        referrer_update = update(User).where(User.user_id == order.referrer_id).values(
            balance=User.balance + int(total_amount * 0.05)
        )
        await session.execute(referrer_update)

    await session.commit()