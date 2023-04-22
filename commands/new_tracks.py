from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, musicapi, config, bot
from objects import globals
from modules import database
from aiogram.utils import markdown
from modules.utils import convert_from_seconds, paginate
import random
from gifs import gifs

chat_id_channel = config["channel_chat_id"]
bot_token = config["telegram_token"]

@dispatcher.message_handler(lambda message: message.text == "🎵 Новинки")
async def new_releases_command(message: Message):
    globals.add_usage_stats()
    try:
        await database.create_user(message.from_user.id)
        test = globals.cache_user_page(message.from_user.id, "new_releases_back_0")
        if globals.cache != None and globals.cache.new_songs_downloaded:
            data = list(paginate(globals.cache.new_songs, globals.config["tracks_on_page"]))[0]
        else:
            new_songs_data = await musicapi.new_songs()
            if new_songs_data is None:
                await message.reply(markdown.escape_md("Нам не удалось найти аудиозаписи."))
                return
            data = list(paginate(new_songs_data["list"], globals.config["tracks_on_page"]))[0]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await message.reply(markdown.escape_md("Нам не удалось найти аудиозаписи."))
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"new_releases_back_0"),
                InlineKeyboardButton("➡️", callback_data=f"new_releases_next_2"))
        
        #await message.answer_video(gif, caption="🎵Новые песни недели:", reply_markup=markup, reply=True)
        await message.answer_video(random.choice(gifs.gifs), caption="🎵Новые песни недели:", reply_markup=markup, reply=True)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("new_releases_next_"))
async def new_releases_next(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        if page == 0:
            return await query.answer(markdown.escape_md("Достигнуто начало списка."))

        new_songs_data = await musicapi.new_songs()
        if new_songs_data is None:
            await query.answer(markdown.escape_md("Достигнут конец списка."))
            return

        data = list(paginate(new_songs_data["list"], globals.config["tracks_on_page"]))
        if page >= len(data):
            return await query.answer(markdown.escape_md("Достигнут конец списка."))

        data = data[page]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await query.answer(markdown.escape_md("Достигнут конец списка."))
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"new_releases_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"new_releases_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("new_releases_back_"))
async def new_releases_back(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)
        page = int(query.data.split("_")[-1])

        if page == 0:
            await query.answer(markdown.escape_md("Достигнуто начало списка."))
            return

        new_songs_data = await musicapi.new_songs()
        if new_songs_data is None:
            await query.answer(markdown.escape_md("Достигнут конец списка."))
            return
        
        data = list(paginate(new_songs_data["list"], globals.config["tracks_on_page"]))
        if len(data) < page:
            return await query.answer(markdown.escape_md("Достигнут конец списка."))

        data = data[page]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await query.answer(markdown.escape_md("Достигнуто начало списка."))
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"new_releases_back_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"new_releases_next_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)