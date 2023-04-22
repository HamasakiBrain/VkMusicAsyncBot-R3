from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, musicapi, config, bot
from objects import globals
from modules import database
from modules.utils import convert_from_seconds, paginate
import random

from gifs import gifs

chat_id_channel = config["channel_chat_id"]
bot_token = config["telegram_token"]

@dispatcher.message_handler(lambda message: message.text == "🎙️ Топ")
async def top_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)

        globals.cache_user_page(message.from_user.id, "top_back_0")
        if globals.cache != None and globals.cache.chart_downloaded:
            data = list(paginate(globals.cache.chart, globals.config["tracks_on_page"]))[0]
        else:
            data = list(paginate((await musicapi.chart())["list"], globals.config["tracks_on_page"]))[0]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await message.reply("Нам не удалось получить ТОП аудиозаписей. Попробуйте снова.", reply=True)
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"top_back_0"),
                InlineKeyboardButton("➡️", callback_data=f"top_next_2"))
        
        await message.answer_video(random.choice(gifs.gifs), caption="🎙️Популярные песни недели:", reply_markup=markup, reply=True)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("top_next_"))
async def top_next(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        if page == 0:
            return await query.answer("Достигнуто начало списка.")

        data = list(paginate((await musicapi.chart())["list"], globals.config["tracks_on_page"]))
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

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"top_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"top_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("top_back_"))
async def top_back(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        if page == 0:
            await query.answer("Достигнуто начало списка.")
            return

        data = list(paginate((await musicapi.chart())["list"], globals.config["tracks_on_page"]))
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

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"top_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"top_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)