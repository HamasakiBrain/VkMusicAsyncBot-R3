import inspect
from logging import Logger
from aiogram import Bot, Dispatcher
from modules.musicapi import MusicAPI

from orm import ModelRegistry
from databases import Database
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Engine
from typing import Optional
from asyncio import sleep
from os.path import isdir, isfile
from os import mkdir
import json
from modules.cache import Cache
from modules.utils import get_audio_url
from aiohttp import ClientSession
from io import BytesIO
import pickle

logger: Logger = None
musicapi: MusicAPI = None

database: Database = None
models: ModelRegistry = None
db_engine: Engine = None

CompleteCache = None

bot: Bot = None
dispatcher: Dispatcher = None
config: dict = None

bot_mention: str = "whoami"

cached_users: list = []
cached_users_states: dict = {}

cached_audio: dict = {}

received_ad: int = -1
ad_content: str = None

is_mass_sending: bool = False
current_ad_sent: int = 0
current_ad_cant_sent: int = 0

current_ip: str = None

cache: Cache = None
users_ids: list = []

musics:dict = {}

# Статистика использования
usage_stats: dict = {}

def add_usage_stats():
    func_name = inspect.stack()[1][3]
    if func_name not in usage_stats: usage_stats[func_name] = 0
    usage_stats[func_name] += 1

async def store_cache():
    while True:
        try:
            if cached_users_states == {}:
                continue

            if not isdir("cache"):
                mkdir("cache")

            # logger.info("Storing cache to disk")
            with open("cache/users_states.json", "w+t", encoding="utf-8") as file:
                json.dump(cached_users_states, file, indent=4)
        except Exception as e:
            logger.exception("An error caused on storing cache to disk!!!", e)
        finally:
            await sleep(10)

def get_user_state(user_id: int) -> Optional[dict]:
    if user_id in cached_users_states:
        return cached_users_states[user_id]
    else: return None

def cache_user_page(user_id: int, page: str):
    if user_id not in cached_users_states:
        cached_users_states[user_id] = { "page": page, "search": None }
    else: cached_users_states[user_id]["page"] = page

def cache_user_search(user_id: int, search: str):
    if user_id not in cached_users_states:
        cached_users_states[user_id] = { "page": None, "search": search }
    else: cached_users_states[user_id]["search"] = search

async def cache_music_charts(seconds:int):
    while True:
        await sleep(seconds)
        charts:list = await musicapi.chart()

        async with ClientSession() as session:
            for chart in charts["list"]:
                async with session.get(get_audio_url(chart["owner_id"], chart["audio_id"], chart["artist"], chart["title"])) as resp:
                    audio = await resp.read()
                    file_bytes = BytesIO(await resp.read())
                    if file_bytes.getbuffer().nbytes / 1024 / 1024 > 50:pass
                    else:
                        with open(r"cache_musics/%s" % f"{chart['artist']} - {chart['title']}.mp3", "wb") as file_write:
                            pickle.dump(audio, file_write)
                            file_write.close()

async def cache_music_new(seconds:int):
    while True:
        await sleep(seconds)
        charts:list = await musicapi.new_songs()
        async with ClientSession() as session:
            for chart in charts["list"]:
                async with session.get(get_audio_url(chart["owner_id"], chart["audio_id"], chart["artist"], chart["title"])) as resp:
                    audio = await resp.read()
                    file_bytes = BytesIO(await resp.read())
                    if file_bytes.getbuffer().nbytes / 1024 / 1024 > 50:pass
                    else:
                        with open(r"cache_musics/%s" % f"{chart['artist']} - {chart['title']}.mp3", "wb") as file_write:
                            pickle.dump(audio, file_write)
                            file_write.close()                   