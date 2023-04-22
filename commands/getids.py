from aiogram.types import Message, InputFile
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config
from objects import globals
from modules import database
from datetime import datetime, timedelta
from modules.utils import random_string
from string import ascii_uppercase
from os import remove

@dispatcher.message_handler(commands="getids")
async def getids_command(message: Message):
    globals.add_usage_stats()
    try:
        globals.add_usage_stats()
        await database.create_user(message.from_user.id)
        if message.from_user.id not in config["admins_telegram_ids"]:
            return

        filename: str = f"{random_string(12, ascii_uppercase)}.txt"
        with open(filename, "w+") as file:
            file.write("\n".join(str(v) for v in await database.get_users_ids()))

        await message.answer_document(InputFile(filename))
        remove(filename)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)