from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, musicapi, config, bot
from objects import globals
from modules import database
from modules.utils import convert_from_seconds, paginate

chat_id_channel = config["channel_chat_id"]
bot_token = config["telegram_token"]

@dispatcher.message_handler(lambda message: message.text == "🎧 ВК")
async def vk_command(message: Message):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(message.from_user.id)

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("Отмена", callback_data="cancel"))
           
        await message.reply(
                "Отправьте мне ссылку на профиль из форматов:\n"
                "```https://vk.com/id1```\n"
                "```https://vk.com/durov```\n"
                "❗️ ***Важно! Аудиозаписи должны быть открыты!***", reply_markup=markup, reply=True
                )
                            
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.message_handler(lambda message: message.text is not None and "vk.com" in message.text)
async def vk_page(message: Message):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(message.from_user.id)

        separated = message.text.split(".com/")
        if len(separated) != 2:
            return

        user_id = None
        if separated[1].startswith("id"): user_id = separated[1].replace("id", "")
        else: user_id = separated[1]

        globals.cache_user_page(message.from_user.id, f"vk_back_{user_id}_0")

        tracks_by_owner = await musicapi.by_owner(user_id)
        print(tracks_by_owner)
        if len(tracks_by_owner) == 0: return await message.reply("Треков не найдено.")
        else: tracks_by_owner = tracks_by_owner["list"]

        data = list(paginate(tracks_by_owner, globals.config["tracks_on_page"]))
        if len(data) == 0: return await message.reply("Треков не найдено.")

        data = data[0]

        tracks: list = []
        for track in data:
            await database.create_audio(track["owner_id"], track["audio_id"], track["artist"], track["title"], track["duration"])
            tracks.append(track)

        if len(tracks) == 0:
            await message.reply("Нам не удалось найти аудиозаписей.", reply=True)
            return

        markup = InlineKeyboardMarkup(row_width=2)
        for track in tracks:
            markup.add(InlineKeyboardButton(f"{track['artist']} - {track['title']} ({convert_from_seconds(track['duration'])})",
                                            callback_data=f"audio_{track['owner_id']}_{track['audio_id']}"))

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"vk_back_{user_id}_0"),
                   InlineKeyboardButton("➡️", callback_data=f"vk_next_{user_id}_2"))

        await message.reply(f"Музыка со страницы", reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("vk_next_"))
async def vk_page_next(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)

        separated = query.data.replace("vk_next_", "").split("_")
        user_id = separated[0]
        page = int(separated[1])

        data = list(paginate((await musicapi.by_owner(user_id))["list"], globals.config["tracks_on_page"]))
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

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"vk_back_{user_id}_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"vk_next_{user_id}_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("vk_back_"))
async def vk_page_back(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(query.from_user.id)

        globals.cache_user_page(query.from_user.id, query.data)

        separated = query.data.replace("vk_back_", "").split("_")
        user_id = separated[0]
        page = int(separated[1])

        if page == 0:
            await query.answer("Достигнуто начало списка.")
            return

        data = list(paginate((await musicapi.by_owner(user_id))["list"], globals.config["tracks_on_page"]))
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

        markup.add(InlineKeyboardButton("⬅️", callback_data=f"vk_back_{user_id}_{page - 1}"),
                   InlineKeyboardButton("➡️", callback_data=f"vk_next_{user_id}_{page + 1}"))

        await query.message.edit_reply_markup(reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)