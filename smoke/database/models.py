from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, BigInteger, func, Float, Integer, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)

class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    maker: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    image: Mapped[str] = mapped_column(String(150))
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer)
    taste: Mapped[str] = mapped_column(Text)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)  # Добавляем поле is_closed

    category: Mapped['Category'] = relationship('Category', backref='products')

class Favourite(Base):
    __tablename__ = 'favourite'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)

    user: Mapped['User'] = relationship('User', backref='favourites')
    product: Mapped['Product'] = relationship('Product', backref='favourites')


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(150), nullable=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(13), nullable=True)
    username: Mapped[str] = mapped_column(String(150), nullable=True)
    spent: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(150), nullable=True)
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=True)

    promocodes: Mapped[list["Promocode"]] = relationship("Promocode", back_populates="user")

class Promocode(Base):
    __tablename__ = 'promocode'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Float, nullable=False)
    discount_type: Mapped[str] = mapped_column(String(10), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.id'), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="promocodes")


class Cart(Base):
    __tablename__ = 'cart'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int]

    user: Mapped['User'] = relationship('User', backref='cart')
    product: Mapped['Product'] = relationship('Product', backref='cart')




class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    referrer_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    order_number: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    maker: Mapped[str] = mapped_column(Text, nullable=False)
    taste: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), default='Не оплачен')
    order_status: Mapped[str] = mapped_column(String(50), default='В обработке')

    product: Mapped['Product'] = relationship('Product', backref='orders')
    user: Mapped['User'] = relationship('User', backref='orders')

class CartItem(Base):
    __tablename__ = 'cart_item'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_time: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # Цена товара на момент добавления в корзину
    added_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())  # Дата добавления товара в корзину
    discount_id: Mapped[int] = mapped_column(ForeignKey('promocode.id', ondelete='SET NULL'), nullable=True)  # Скидка, примененная к товару

    user: Mapped['User'] = relationship('User', backref='cart_items')
    product: Mapped['Product'] = relationship('Product', backref='cart_items')
    discount: Mapped['Promocode'] = relationship('Promocode', backref='cart_items')