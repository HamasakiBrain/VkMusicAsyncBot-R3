import asyncio
import logging
import json

from os import path, mkdir

from aiohttp import ClientSession

from aiogram import Bot, Dispatcher
from aiogram.types import ParseMode, Message
from aiogram.utils.exceptions import ValidationError, Unauthorized
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from databases import Database
from orm import ModelRegistry
from sqlalchemy import MetaData, create_engine

from modules.musicapi import MusicAPI
from objects import globals
from modules.cache import Cache

from middleware.RateLimitMiddleware import RateLimitMiddleware

from aiohttp import ClientSession

async def main():
    # Логгер
    globals.logger = logging.getLogger()
    globals.logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s - [%(module)s %(funcName)s %(lineno)d] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    globals.logger.addHandler(ch)

    # Конфигурация
    if not path.isfile("config.json"):
        with open("config.json", "w", encoding="utf-8") as config_file:
            json.dump({
                "telegram_token": "",

                "api_url": "",
                "api_key": "",
                "api_app_id": 0,

                "tracks_on_page": 10,

                "anticaptcha_key": "",

                "admins_telegram_ids": [],
                "require_subscription": False,
                "require_subscription_channel": 0,
                "listing_cache_cooldown": 30
            }, config_file, indent=4)

            globals.logger.error("Config file not found. Created a new one. Please fill it and restart bot.")
            exit(0)
    else:
        with open("config.json", "r", encoding="utf-8") as config_file:
            globals.config = json.load(config_file)
            logging.info("Configuration loaded!")

    # IP
    async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
        async with session.get(f"https://wowbot.xn--41a.wiki/get_my_ip.php") as response:
            globals.current_ip = await response.text()
    globals.logger.info(f"Current IP is - {globals.current_ip}")

    # ВК
    globals.musicapi = MusicAPI(globals.config["api_url"], globals.config["api_key"], globals.config["api_app_id"])

    globals.cache = Cache(loop, globals.logger, globals.musicapi, globals.config["listing_cache_cooldown"])

    # База данных
    globals.database = Database("sqlite:///NewVkMusic.sqlite")
    globals.models = ModelRegistry(globals.database)

    from db_models.User import User
    from db_models.Audio import Audio
    from db_models.UserAudio import UserAudio
    from db_models.AudioDownloads import AudioDownloads

    await globals.models.create_all()

    from modules.CompleteCache import CompleteCache
    globals.CompleteCache = CompleteCache()
    await globals.CompleteCache.load()

    globals.cached_users = [{"user_id": user.user_id, "created": user.created, "last_seen": user.last_seen, "is_banned": False} for user in await User.objects.all()]

    globals.users_ids = [user.user_id for user in await User.objects.all()]

    for audio in await Audio.objects.all():
        globals.cached_audio[f"{audio.owner_id}_{audio.audio_id}"] = {
            "owner_id": audio.owner_id,
            "audio_id": audio.audio_id,

            "artist": audio.artist,
            "title": audio.title,
            "duration": audio.duration
        }

    # Получившие рассылку
    if path.isdir("cache") and path.isfile("cache/received_ad.txt"):
        with open("cache/received_ad.txt", "r") as file:
            globals.received_ad = int(file.read().replace("\n", ""))

    # Стейты
    if path.isdir("cache") and path.isfile("cache/users_states.json"):
        with open("cache/users_states.json", "r", encoding="utf-8") as file:
            globals.cached_users_states = json.load(file)

    # Create folder for cache musics
    if not path.isdir('cache_musics'):
        mkdir('cache_musics')

    # Телеграмм
    try:
        globals.bot = Bot(token=globals.config["telegram_token"], parse_mode=ParseMode.MARKDOWN)
        globals.dispatcher = Dispatcher(globals.bot, storage=MemoryStorage())
        globals.dispatcher.middleware.setup(RateLimitMiddleware())
        globals.dispatcher.errors_handler()

        bot_info = await globals.bot.get_me()
        globals.bot_mention = f"@{bot_info.username}".replace("_", "\_")
        globals.logger.info(f"Bot @{bot_info.username} started!")

        import commands
        msg = ("Подписка не активирована(obyzaon) Т.к бот был перезапущен!\n"
               "Активация: /obyazon")
        admin_id = globals.config["admins_telegram_ids"][1]
        async with ClientSession() as session:
            await globals.bot.send_message(admin_id, msg)
            await session.close()

        await globals.dispatcher.start_polling()
    except (Unauthorized, ValidationError):
        globals.logger.error("Can't start bot because telegram token validation failure. Check your telegram_token field in config file.")
        exit(0)

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(globals.cache_music_charts(43200))
        loop.create_task(globals.cache_music_new(43200))
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        exit(0)
