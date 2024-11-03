# from string import punctuation

# from aiogram import F, Bot, types, Router
# from aiogram.filters import Command

# from filters.chat_types import ChatTypeFilter



# user_group_router = Router()
# user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
# user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


# @user_group_router.message(Command("admin"))
# async def get_admins(message: types.Message, bot: Bot):
#     chat_id = message.chat.id
#     admins_list = await bot.get_chat_administrators(chat_id)
#     #просмотреть все данные и свойства полученных объектов
#     #print(admins_list)
#     # Код ниже это генератор списка, как и этот x = [i for i in range(10)]
#     admins_list = [
#         member.user.id
#         for member in admins_list
#         if member.status == "creator" or member.status == "administrator"
#     ]
#     bot.my_admins_list = admins_list
#     if message.from_user.id in admins_list:
#         await message.delete()
#     #print(admins_list)


# def clean_text(text: str):
#     return text.translate(str.maketrans("", "", punctuation))


from string import punctuation

from aiogram import F, Bot, types, Router
from aiogram.filters import Command

from filters.chat_types import ChatTypeFilter



user_group_router = Router()
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))
user_group_router.edited_message.filter(ChatTypeFilter(["group", "supergroup"]))


@user_group_router.message(Command("admin"))
async def get_admins(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    #просмотреть все данные и свойства полученных объектов
    #print(admins_list)
    # Код ниже это генератор списка, как и этот x = [i for i in range(10)]
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.answer("Список администраторов был обновлен!")
    #print(admins_list)

@user_group_router.message(Command("clearadmins"))
async def clear_admins_cmd(message: types.Message, bot: Bot):
    # Проверка, что пользователь является админом
    if message.from_user.id in bot.my_admins_list:
        bot.my_admins_list.clear()
        await message.answer("Список админов очищен.")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")

def clean_text(text: str):
    return text.translate(str.maketrans("", "", punctuation))


