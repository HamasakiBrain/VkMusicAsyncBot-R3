from objects.globals import dispatcher, config
from aiogram.types import Message
from objects import globals

@dispatcher.message_handler(commands="obyazon")
async def on_obyaz(message: Message):
    if message.from_user.id in config["admins_telegram_ids"]:
        globals.config["require_subscription"] = True
        await message.answer(
            "Подписка активирована"
        )

@dispatcher.message_handler(commands="obyazoff")
async def off_obyaz(message: Message):
    if message.from_user.id in config["admins_telegram_ids"]:
        globals.config["require_subscription"] = False
        await message.answer(
            "Подписка деактивирована"
        )