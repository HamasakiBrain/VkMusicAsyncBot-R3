from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, CompleteCache, config, bot
from objects import globals
from modules import database
from io import BytesIO
from aiohttp import ClientSession
from modules.utils import get_audio_url
import urllib.request
from os import listdir
import json 

from aiohttp import ClientSession

from db_models.User import User

bot_token = config["telegram_token"]
chat_id_channel = config["channel_chat_id"]

@dispatcher.callback_query_handler(lambda query: query.data.startswith("audio_"))
async def download(query: CallbackQuery):
    
    globals.add_usage_stats()
    try:
        await database.create_user(query.from_user.id)   

        if globals.config["require_subscription"]:
            flag:bool = True
            try:
                #status = (await globals.bot.get_chat_member(globals.config["require_subscription_channel"], query.from_user.id)).status
                check_url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={chat_id_channel}&user_id={query.from_user.id}"

                async with ClientSession() as session:
                    res = await session.get(check_url)
                    res = json.loads(await res.text())
                    await session.close()

                if res["result"]["status"] == "member" or res["result"]["status"] == "creator":pass
                elif res["result"]["status"] == "left":
                    with open(r"cache/sub_cache.json", "r", encoding="utf-8") as read_sub_cache:
                        sub_cache = json.loads(read_sub_cache.read())
                    
                    if not str(query.from_user.id) in list(sub_cache.keys()):
                        sub_cache[str(query.from_user.id)] = 1

                    if sub_cache[str(query.from_user.id)] == 0:
                        flag = False

                    cic = chat_id_channel.replace("@", "")
                    check_sub = InlineKeyboardMarkup(
                        inline_keyboard=[
                            [InlineKeyboardButton(text="✅Проверить подписку!✅", callback_data=f"check-sub_{query.from_user.id}")]
                        ]
                    )
                    
                    if flag:
                        await bot.send_message(
                                query.from_user.id, 
                                f"Осталось {sub_cache[str(query.from_user.id)]} из 1\n\n"
                                f"Подпишитесь на канал [СНГ сегодня | Горячие новости ](https://t.me/{cic}), чтобы получить полный доступ ко всей музыке!✌️🔥",
                                reply_markup=check_sub
                                )
                        sub_cache[str(query.from_user.id)] -= 1
                    else:
                        return await bot.send_message(
                                query.from_user.id, 
                                f"Подпишитесь на канал [СНГ сегодня | Горячие новости ](https://t.me/{cic}), чтобы получить полный доступ ко всей музыке!✌️🔥",
                                reply_markup=check_sub
                                )

                    with open(r"cache/sub_cache.json", "w") as write_sub_cache:
                        write_sub_cache.write(json.dumps(sub_cache))
                        write_sub_cache.close()

                    read_sub_cache.close()
            except Exception as e:
                print(e)     

        audio_id = query.data.replace("audio_", "")
        audio_data = audio_id.split("_")
        # db_audio = await database.get_audio(int(audio_data[0]), int(audio_data[1]))
        db_audio = await globals.musicapi.get_audio(int(audio_data[0]), int(audio_data[1]))

        if db_audio is None:
            return await query.answer("Ошибка! Трек не найден. Возможно он был удалён.")
     
        try:
            img = urllib.request.urlopen(db_audio["image_68"]).read()
        except ValueError:img=None

        markup = InlineKeyboardMarkup(row_width=2)

        if await database.user_has_audio(query.from_user.id, int(audio_data[0]), int(audio_data[1])):
            markup.add(InlineKeyboardButton("🗑 Удалить из аудиозаписей", callback_data=f"my_audio_remove_{audio_id}"))
        else: markup.add(InlineKeyboardButton("➕ Добавить в аудиозаписи", callback_data=f"my_audio_add_{audio_id}"))

        markup.add(InlineKeyboardButton("🎧 Мои аудиозаписи", callback_data=f"my_audio_show"))

        await database.add_downloaded_audio(db_audio["owner_id"], db_audio["audio_id"])

        audio_name = f"{db_audio['artist']} - {db_audio['title']}.mp3"
        await globals.bot.send_chat_action(query.message.chat.id, 'upload_voice')
        
        if audio_name in list(sorted(listdir("cache_musics"))):
            audio = open(r"cache_musics/%s" % audio_name, "rb").read()
        
            await globals.bot.send_audio(
                    query.message.chat.id, 
                    audio=audio,
                    caption=f"🎶 Ищешь популярные и новые песни? [ЖМИ!](https://t.me/wowmuz_play)",
                    title=audio_name,
                    thumb=img,
                    reply_markup=markup 
            )
               
        else:         
            async with ClientSession() as session:
                async with session.get(get_audio_url(db_audio["owner_id"], db_audio["audio_id"], db_audio["artist"], db_audio["title"])) as resp:
                    text = await resp.read()
                    file_bytes = BytesIO(await resp.read())
                    if file_bytes.getbuffer().nbytes / 1024 / 1024 > 50:
                        return await query.answer("Файл слишком большой и нам не удалось загрузить его в Telegram.")

                    await globals.bot.send_audio(
                        query.message.chat.id, 
                        InputFile(file_bytes, filename=f"{db_audio['artist']} - {db_audio['title']}"), 
                        caption=f"🎶 Ищешь популярные и новые песни? [ЖМИ!](https://t.me/wowmuz_play)",
                        title=audio_name,
                        thumb=img,
                        reply_markup=markup
                    )       

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(lambda query: query.data.startswith(("check-sub")))
async def check_sub(query: CallbackQuery):
    user_id = query.data.split("_")[1]

    check_url = f"https://api.telegram.org/bot{bot_token}/getChatMember?chat_id={chat_id_channel}&user_id={user_id}"

    async with ClientSession() as session:
        res = await session.get(check_url)
        res = json.loads(await res.text())

    if res["result"]["status"] == "member" or res["result"]["status"] == "creator":
        await bot.send_message(
                query.message.chat.id,
                text="Супер! Вам предоставлен полный доступ ко всей музыке! Приятного пользования!🔥"
                )

    elif res["result"]["status"] == "left":
        await bot.send_message(
                query.message.chat.id,
                text="Вы не подписались на канал. Попробуйте снова!",
                )
