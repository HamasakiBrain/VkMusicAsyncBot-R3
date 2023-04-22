from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, musicapi, config
from objects import globals
from modules import database
from modules.utils import convert_from_seconds, paginate
from gifs import gifs
import random

chat_id_channel = config["channel_chat_id"]
bot_token = config["telegram_token"]

@dispatcher.message_handler(lambda message: message.text == "🔍 Поиск")
async def search_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🎧 Мои аудиозаписи", callback_data="my_audio_show"))

        #await message.reply("🔍 Введите название песни или имя исполнителя:", reply_markup=markup, reply=True)    
        await message.answer_video(random.choice(gifs.gifs), caption="🔍 Введите название песни или имя исполнителя:", reply_markup=markup, reply=True)      

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.message_handler()
async def search(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)

        globals.cache_user_page(message.from_user.id, "search_back_0")
        globals.cache_user_search(message.from_user.id, message.text)

        try:
            data = list(paginate((await musicapi.search(message.text))["list"], globals.config["tracks_on_page"]))
        except TypeError: data = []

        if len(data) == 0:
            await message.reply("Нам не удалось найти треков по вашему запросу.")
            return
        else:
            data = data[0]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await message.reply("Нам не удалось найти аудиозаписи по вашему запросу.", reply=True)
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"search_back_0"),
                InlineKeyboardButton("➡️", callback_data=f"search_next_2"))

        await message.reply("Треки по вашему запросу", reply_markup=markup, reply=True)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("search_next_"))
async def search_next(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        state = globals.get_user_state(query.from_user.id)
        if state is None: return

        if state["search"] is None:
            return await query.answer("Ошибка чтения поискового запроса. Попробуйте снова.")

        data = list(paginate((await musicapi.search(state["search"]))["list"], globals.config["tracks_on_page"]))
        if page >= len(data):
            return await query.answer("Достигнут конец списка.")

        data = data[page]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await query.answer("Достигнут конец списка.")
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"search_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"search_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("search_back_"))
async def search_back(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        if page == 0:
            await query.answer("Достигнуто начало списка.")
            return

        state = globals.get_user_state(query.from_user.id)
        if state is None: return
        try:
            data = list(paginate((await musicapi.search(state["search"]))["list"], globals.config["tracks_on_page"]))
        except TypeError: data = []
        
        if len(data) < page:
            return await query.answer("Достигнут конец списка.")

        data = data[page]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await query.answer("Достигнуто начало списка.")
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"search_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"search_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)