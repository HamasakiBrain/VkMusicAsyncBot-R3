from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config
from objects import globals
from modules import database
from datetime import datetime, timedelta

@dispatcher.message_handler(commands="stat889")
async def refs_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)
        refs: dict = await database.get_refs()

        text: str = "Статистика рефералок:\n"
        for key in refs.keys():
            text += f"{key}: {refs[key]}\n"

        await message.answer(text,
                             reply=True)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.message_handler(commands="refdel9")
async def remove_ref_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)
        if message.from_user.id not in config["admins_telegram_ids"]:
            return

        args: list = message.text.split()
        if len(args) == 1:
            return await message.reply("Вы не указали код рефералки.", reply=True)

        refs: dict = await database.get_refs()
        if args[1] not in refs.keys():
            return await message.reply("Рефералка не найдена.", reply=True)

        await database.remove_ref(args[1])
        await message.answer("Удалено!", reply=True)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.message_handler(commands="refdel0")
async def clear_ref_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)
        if message.from_user.id not in config["admins_telegram_ids"]:
            return

        await database.clear_refs()
        await message.answer("Очищено!", reply=True)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)