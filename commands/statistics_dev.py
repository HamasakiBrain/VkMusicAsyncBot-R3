from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config
from objects import globals
from modules import database

@dispatcher.message_handler(commands="devstats888")
async def devstats_command(message: Message):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(message.from_user.id)
        if message.from_user.id not in config["admins_telegram_ids"]:
            return

        usage_stats_text: str = ""
        for func_name in globals.usage_stats:
            usage_stats_text += f"{func_name}: {globals.usage_stats[func_name]}\n".replace("_", "\_")

        await message.answer(f"CompleteCache:\n"
                             f"users\_ids: {len(globals.CompleteCache.users_ids)}\n"
                             f"users: {len(globals.CompleteCache.users)}\n"
                             f"user\_audios: {len(globals.CompleteCache.user_audios)}\n"
                             f"not\_banned: {len(await database.get_not_banned())}\n\n"
                             f""
                             f"Статистика использования:\n{usage_stats_text}",

                             reply=True)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)