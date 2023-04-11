from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger
#from modules import database
from objects import globals

@dispatcher.message_handler(lambda message: message.text == "👍Полезные сервисы")
async def information_command(message: Message):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(message.from_user.id)

        await message.answer(   
                "*ПОЛЕЗНЫЕ СЕРВИСЫ!* 😜\n"
                "🔈 Новинки и популярная музыка: @wowmuz_play\n\n"
                "📰 Горячие новости СНГ! Будь в курсе! @today_sng\n\n"
                "💸 Нужны деньги??? Этот бот поможет: @mydengibot\n\n"
                "👔 Админ: @mikhailrusso",
                reply=True, 
                parse_mode="html"
                )

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)