from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from db_models.Audio import Audio
from objects.globals import dispatcher, logger
from objects import globals
from modules import database
from modules.utils import convert_from_seconds

@dispatcher.callback_query_handler(lambda query: query.data.startswith("my_audio_show"))
async def my_audio_show(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)
        globals.cache_user_page(query.from_user.id, query.data)

        audios = await database.user_get_audios(query.from_user.id)
        if len(audios) == 0:
            return await query.answer("Ваш список аудиозаписей - пуст.")

        markup = InlineKeyboardMarkup(row_width=2)
        for track in audios:
            
            # cached = globals.cached_audio[f"{track.owner_id}_{track.audio_id}"]
            cached = await Audio.objects.filter(owner_id=track.owner_id, audio_id=track.audio_id).all()
            # cached = await Audio.objects.get(owner_id=track.owner_id, audio_id=track.audio_id)
            markup.add(InlineKeyboardButton(f"{cached[0].artist} - {cached[0].title} ({convert_from_seconds(cached[0].duration)})",
                                            callback_data=f"audio_{track.owner_id}_{track.audio_id}"))
            
        await globals.bot.send_message(query.message.chat.id, "В данном разделе находится ваша музыка 🎶", reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("my_audio_add_"))
async def my_audio_add(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)
        globals.cache_user_page(query.from_user.id, query.data)

        audio_data = query.data.replace("my_audio_add_", "").split("_")
        if await database.user_has_audio(query.from_user.id, int(audio_data[0]), int(audio_data[1])):
            return await query.answer("Эта аудиозапись уже в вашем списке!")

        await database.user_add_audio(query.from_user.id, int(audio_data[0]), int(audio_data[1]))

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("🗑 Удалить из аудиозаписей", callback_data=f"my_audio_remove_{audio_data[0]}_{audio_data[1]}"))
        markup.add(InlineKeyboardButton("🎧 Мои аудиозаписи", callback_data=f"my_audio_show"))

        # state = globals.get_user_state(query.from_user.id)
        # if state is not None and state["page"] is not None:
        #     markup.add(InlineKeyboardButton("↩️ Вернуться к запросу", callback_data=state["page"]))

        await query.message.edit_reply_markup(markup)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith("my_audio_remove_"))
async def my_audio_remove(query: CallbackQuery):
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)
        globals.cache_user_page(query.from_user.id, query.data)

        audio_data = query.data.replace("my_audio_remove_", "").split("_")
        if await database.user_has_audio(query.from_user.id, int(audio_data[0]), int(audio_data[1])) is False:
            return await query.answer("Этой аудиозаписи нет в вашем списке!")

        await database.user_remove_audio(query.from_user.id, int(audio_data[0]), int(audio_data[1]))

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(InlineKeyboardButton("➕ Добавить в аудиозаписи", callback_data=f"my_audio_add_{audio_data[0]}_{audio_data[1]}"))
        markup.add(InlineKeyboardButton("🎧 Мои аудиозаписи", callback_data=f"my_audio_show"))

        # state = globals.get_user_state(query.from_user.id)
        # if state is not None and state["page"] is not None:
        #     markup.add(InlineKeyboardButton("↩️ Вернуться к запросу", callback_data=state["page"]))

        await query.message.edit_reply_markup(markup)

        await query.message.edit_reply_markup(markup)
    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)