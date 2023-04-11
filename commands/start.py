from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config, CompleteCache, bot
from objects import globals

import json
from aiohttp import ClientSession

chat_id_channel = config["channel_chat_id"]
bot_token = config["telegram_token"]

@dispatcher.message_handler(commands="start")
async def start_command(message: Message):
    globals.add_usage_stats()
    try:
        data: list = message.text.split()
        # if len(data) > 1: await database.create_user(message.from_user.id, data[1])
        # else: await database.create_user(message.from_user.id)

        if len(data) > 1: await CompleteCache.create_user(message.from_user.id, data[1])
        else: await CompleteCache.create_user(message.from_user.id)

        """
        if globals.config["status_obyaz"] == True:
            check_url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={chat_id_channel}&user_id={message.from_user.id}"
            async with ClientSession() as session:
                res = await session.get(check_url)
                res = json.loads(await res.text())
        
            if res["result"]["status"] == "member" or res["result"]["status"] == "creator":
        """
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add(KeyboardButton("🎙️ Топ"), KeyboardButton("🎵 Новинки"),
                KeyboardButton("🎧 ВК"), KeyboardButton("🔍 Поиск"))

        if message.from_user.id in config["admins_telegram_ids"]:
            markup.add(KeyboardButton("👍Полезные сервисы"), KeyboardButton("🔥 Статистика"))
        else: markup.add(KeyboardButton("👍Полезные сервисы"))

        await message.answer(
                "Поиск песен - /search\n"
                "Популярные песни - /top\n"
                "Новые песни - /new\n"
                "Музыка из ВК страницы - /vk\n\n"
                "Мои аудиозаписи - /mymusic\n"
                "Или просто ВОСПОЛЬЗУЙТЕСЬ нашим меню:"
                "[ ](https://telegra.ph/file/e21fb04bef6c4e0b6bddf.jpg)",
                reply_markup=markup,
                reply=True
        )

        """
            elif res["result"]["status"] == "left":
                check_sub = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="✅Проверить подписку!✅", callback_data=f"check-sub_{message.from_user.id}")]
                    ]
                )

                await message.answer(
                        f"Подпишитесь на канал [СНГ сегодня | Горячие новости ](https://t.me/today_sng), чтобы получить полный доступ ко всей музыке!✌️🔥",
                        reply_markup=check_sub
                        )
        else:
            markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add(KeyboardButton("🎙️ Топ"), KeyboardButton("🎵 Новинки"),
                    KeyboardButton("🎧 ВК"), KeyboardButton("🔍 Поиск"))

            if message.from_user.id in config["admins_telegram_ids"]:
                markup.add(KeyboardButton("ℹ️ Информация"), KeyboardButton("🔥 Статистика"))
            else: markup.add(KeyboardButton("ℹ️ Информация"))

            await message.answer(
                    "Поиск песен - /search\n"
                    "Популярные песни - /top\n"
                    "Новые песни - /new\n"
                    "Музыка из ВК страницы - /vk\n\n"
                    "Мои аудиозаписи - /mymusic\n"
                    "Или просто ВОСПОЛЬЗУЙТЕСЬ нашим меню:"
                    "[ ](https://telegra.ph/file/e21fb04bef6c4e0b6bddf.jpg)",
                    reply_markup=markup,
                    reply=True)       
        """

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith(("check-sub")))
async def check_sub(query: CallbackQuery):
    user_id = query.data.split("_")[1]

    check_url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={chat_id_channel}&user_id={user_id}"

    async with ClientSession() as session:
        res = await session.get(check_url)
        res = json.loads(await res.text())

    if res["result"]["status"] == "member" or res["result"]["status"] == "creator":
        await bot.send_message(
                query.message.chat.id,
                text="Супер! Вам предоставлен полный доступ ко всей музыке! Приятного пользования!🔥"
                )

    elif res["result"]["status"] == "left":
        await bot.send_message(
                query.message.chat.id,
                text="Вы не подписались на канал. Попробуйте снова!",
                )