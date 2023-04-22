from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config
from objects import globals
from modules import database
from db_models.User import User

from datetime import datetime, timedelta

@dispatcher.message_handler(commands="stat888")
@dispatcher.message_handler(lambda message: message.text == "🔥 Статистика")
async def stats_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)
        await message.answer(f"Пользователей - {(await User.objects.count())}\n"
                             f"Активных за 24 часа - {await database.last_day_users()}\n"
                             f"Новых за 24 часа - {await database.last_day_new_users()}\n\n"
                             f"Рассылка:\n"
                             f"Получили последнюю - {'рассылка не проводилась' if globals.received_ad == -1 else globals.received_ad}\n"
                             f"Сейчас проводится: {'Да' if globals.is_mass_sending else 'Нет'}\n"
                             f"Уже отправлено: {globals.current_ad_sent}\n"
                             f"Не удалось отправить: {globals.current_ad_cant_sent}\n\n"
                             f"Песни:\n"
                             f"Всего загрузок - {await database.total_downloads()}\n"
                             f"Загрузок за 24 часа - {await database.last_day_downloads()}",

                             reply=True)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)