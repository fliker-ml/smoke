import math
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from database.models import  Cart, Category, Product, User, Promocode, Favourite #, Banner
from typing import List, Tuple
############### Работа с баннерами (информационными страницами) ###############

# async def orm_add_banner_description(session: AsyncSession, data: dict):
#     #Добавляем новый или изменяем существующий по именам
#     #пунктов меню: main, about, cart, shipping, payment, catalog
#     query = select(Banner)
#     result = await session.execute(query)
#     if result.first():
#         return
#     session.add_all([Banner(name=name, description=description) for name, description in data.items()]) 
#     await session.commit()


# async def orm_change_banner_image(session: AsyncSession, name: str, image: str):
#     query = update(Banner).where(Banner.name == name).values(image=image)
#     await session.execute(query)
#     await session.commit()


# async def orm_get_banner(session: AsyncSession, page: str):
#     query = select(Banner).where(Banner.name == page)
#     result = await session.execute(query)
#     return result.scalar()


# async def orm_get_info_pages(session: AsyncSession):
#     query = select(Banner)
#     result = await session.execute(query)
#     return result.scalars().all()


############################ Категории ######################################

async def orm_get_categories(session: AsyncSession):
    query = select(Category)
    result = await session.execute(query)
    return result.scalars().all()

async def orm_create_categories(session: AsyncSession, categories: list):
    query = select(Category)
    result = await session.execute(query)
    if result.first():
        return
    session.add_all([Category(name=name) for name in categories]) 
    await session.commit()

############ Админка: добавить/изменить/удалить товар ########################

async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        description=data["description"],
        maker=data["maker"],
        price=float(data["price"]),
        image=data["image"],
        category_id=int(data["category"]),
        quantity=int(data["quantity"]),
        taste=data["taste"],
        is_closed=bool(data["is_closed"]),
    )
    session.add(obj)
    await session.commit()

# async def get_products_with_tastes(maker: str, session: AsyncSession):
#     query = select(Product.id, Product.taste).where(Product.maker == maker)
#     result = await session.execute(query)
#     products_with_tastes = result.all()
#     return products_with_tastes

async def orm_get_products(session: AsyncSession, category_id):
    query = select(Product).where(Product.category_id == int(category_id))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            maker=data["maker"],
            price=float(data["price"]),
            image=data["image"],
            category_id=int(data["category"]),
            quantity=int(data["quantity"]),
            taste=data["taste"],
            is_closed=bool(data["is_closed"]),
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_get_makers_by_category(category_id: int, session: AsyncSession, in_stock: bool = False):
    query = select(Product.maker).filter(Product.category_id == category_id)
    if in_stock:
        query = query.filter(Product.quantity > 1)
    result = await session.execute(query)
    makers = result.scalars().unique().all()
    return [Product(maker=maker) for maker in makers]


# async def get_products_with_tastes(maker: str, session: AsyncSession, in_stock: bool = False):
#     query = select(Product.id, Product.taste).filter(Product.maker == maker)
#     if in_stock:
#         query = query.filter(Product.quantity > 1)
#     result = await session.execute(query)
#     products = result.all()
#     return products
async def get_products_with_tastes(maker: str, session: AsyncSession, in_stock: bool = True) -> List[Tuple[int, str, str]]:
    query = select(Product.id, Product.name, Product.taste, Product.quantity).filter(Product.maker == maker, Product.is_closed == False)
    if in_stock:
        query = query.filter(Product.quantity > 0)
    result = await session.execute(query)
    return result.fetchall()

async def get_products_with_tastes_admin(maker: str, session: AsyncSession) -> List[Tuple[int, str, str, bool]]:
    query = select(Product.id, Product.name, Product.taste, Product.is_closed).filter(Product.maker == maker)
    result = await session.execute(query)
    return result.fetchall()
##################### ЮЗЕР  #####################################

async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    username: str | None = None,
    spent: float = 0.0,
    status: str = "Прохожий",
    referrer_id: int | None = None,
    balance: int = 0
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, first_name=first_name, last_name=last_name, phone=phone, username=username,
                 spent=spent, status=status, referrer_id=referrer_id, balance=balance)
        )
        await session.commit()

async def get_user_spent(session: AsyncSession, user_id: int) -> float:
    query = select(User.spent).where(User.user_id == user_id)
    result = await session.execute(query)
    spent = result.scalar()
    return spent if spent is not None else 0.0

async def get_user_status(session: AsyncSession, user_id: int) -> str:
    query = select(User.status).where(User.user_id == user_id)
    result = await session.execute(query)
    status = result.scalar()
    return status if status is not None else "Прохожий"

async def get_all_user_ids(session: AsyncSession) -> list[int]:
    query = select(User.user_id)
    result = await session.execute(query)
    user_ids = result.scalars().all()
    return user_ids

async def count_referrals(session: AsyncSession, user_id: int) -> int:
    query = select(func.count(User.id)).where(User.referrer_id == user_id)
    result = await session.execute(query)
    count = result.scalar()
    return count if count is not None else 0

async def update_user_status(session: AsyncSession, user_id: int, status: str):
    stmt = update(User).where(User.user_id == user_id).values(status=status)
    await session.execute(stmt)
    await session.commit()

async def get_user_balance(session: AsyncSession, user_id: int) -> int:
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar()
    if user:
        return user.balance or 0
    else:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")

async def update_user_balance(session: AsyncSession, user_id: int, amount: int):
    stmt = select(User).where(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar()
    if user:
        if user.balance is None:
            user.balance = 0
        user.balance += amount
        await session.commit()
    else:
        await session.rollback()
        raise ValueError(f"Пользователь с ID {user_id} не найден.")
    
async def update_user_spent(session: AsyncSession, user_id: int, amount_spent: float):
    stmt = select(User).filter(User.user_id == user_id)
    result = await session.execute(stmt)
    user = result.scalar()

    if user:
        user.spent += amount_spent
        await session.commit()
    else:
        raise ValueError("User not found")
    
async def update_product_quantity(session: AsyncSession, product_id: int, quantity: int):
    stmt = select(Product).filter(Product.id == product_id)
    result = await session.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        raise ValueError("Product not found")

    if product.quantity < quantity:
        raise ValueError("Not enough quantity on stock")

    product.quantity -= quantity
    await session.commit()

async def get_user_favourites(session: AsyncSession, user_id: int):
    stmt = select(Favourite).filter(Favourite.user_id == user_id).options(selectinload(Favourite.product))
    result = await session.execute(stmt)
    favourites = result.scalars().all()
    return [favourite.product for favourite in favourites]


######################## Работа с корзинами #######################################

async def orm_add_to_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()
    if cart:
        cart.quantity += 1
        await session.commit()
        return cart
    else:
        session.add(Cart(user_id=user_id, product_id=product_id, quantity=1))
        await session.commit()



async def orm_get_user_carts(session: AsyncSession, user_id):
    query = select(Cart).filter(Cart.user_id == user_id).options(joinedload(Cart.product))
    result = await session.execute(query)
    return result.scalars().all()


async def orm_delete_from_cart(session: AsyncSession, user_id: int, product_id: int):
    query = delete(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    await session.execute(query)
    await session.commit()


async def orm_reduce_product_in_cart(session: AsyncSession, user_id: int, product_id: int):
    query = select(Cart).where(Cart.user_id == user_id, Cart.product_id == product_id)
    cart = await session.execute(query)
    cart = cart.scalar()

    if not cart:
        return
    if cart.quantity > 1:
        cart.quantity -= 1
        await session.commit()
        return True
    else:
        await orm_delete_from_cart(session, user_id, product_id)
        await session.commit()
        return False
    


################################





async def orm_get_products_by_maker(maker: str, session: AsyncSession):
    products = (await session.execute(select(Product).filter_by(maker=maker))).scalars().all()
    return products



    


##################### промокод ###########################

async def delete_promo_code(session: AsyncSession, promo_code: str):
    stmt = delete(Promocode).where(Promocode.name == promo_code)
    await session.execute(stmt)
    await session.commit()