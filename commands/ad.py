from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID
from objects.globals import dispatcher, logger, config
from objects import globals
from modules import database
from os.path import isdir, isfile
from os import mkdir
from asyncio import sleep

@dispatcher.message_handler(commands="ad")
async def ad_command(message: Message):
    '''
    Mailing function
    '''

    globals.add_usage_stats()
    try:
        await globals.CompleteCache.create_user(message.from_user.id)

        #IF not admin
        if message.from_user.id not in config["admins_telegram_ids"]:
            return

        #If the mailing goes
        if globals.is_mass_sending:
            await message.reply("В данный момент уже проводится рассылка. Подождите пока она закончится.")
            return 

        #Takes content
        content = message.text.replace("/ad", "").strip()
        if len(content) == 0:
            await message.reply("Вы забыли указать текст для рассылки!")
            return

        globals.ad_content = content

        if "\nКнопка: " in content:
            text_and_button = content.split("\nКнопка: ")
            text_and_url = text_and_button[1].split(" | ")

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text_and_url[0], url=text_and_url[1]))
            markup.add(InlineKeyboardButton("Начать рассылку", callback_data="ad_verify"), InlineKeyboardButton("Отмена", callback_data="cancel"))

            try: await message.reply(text_and_button[0], reply_markup=markup)
            except: await message.reply("Ошибка формирования сообщения.")
        else:
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("Начать рассылку", callback_data="ad_verify"), InlineKeyboardButton("Отмена", callback_data="cancel"))
            await message.reply(content, reply_markup=markup)

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)

@dispatcher.callback_query_handler(text="ad_verify")
async def ad_callback(query: CallbackQuery):
    try:
        await globals.CompleteCache.create_user(query.from_user.id)

        #IF not admin
        if query.from_user.id not in config["admins_telegram_ids"]:
            return

        globals.is_mass_sending = True
        counter: int = 0

        banned_users: list = []
        res = await database.get_not_banned()

        content = globals.ad_content

        if "\nКнопка: " in content:
            text_and_button = content.split("\nКнопка: ")
            text_and_url = text_and_button[1].split(" | ")

            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton(text_and_url[0], url=text_and_url[1]))

            for index, user in enumerate(res):
                try:
                    print(f"Sending {index}")
                    await globals.bot.send_message(user.user_id, text_and_button[0], reply_markup=markup)
                    counter += 1
                    globals.current_ad_sent = counter

                    if index != 0 and index % 25 == 0:
                        await sleep(1)
                except:
                    print(f"Error on {index}")
                    globals.current_ad_cant_sent += 1
                    banned_users.append(user.user_id) 
                    
        else:
            for index, user in enumerate(res):
                try:
                    await globals.bot.send_message(user.user_id, content)
                    counter += 1
                    globals.current_ad_sent = counter
                    if index != 0 and index % 25 == 0:
                        await sleep(1)
                except:
                    globals.current_ad_cant_sent += 1
                    banned_users.append(user.user_id)

        #await query.answer("End mailing!")
        await database.set_banned(banned_users)
        globals.is_mass_sending = False
        globals.current_ad_sent = 0
        globals.current_ad_cant_sent = 0
        #await globals.bot.delete_message(query.from_user.id, query.message.message_id)
        globals.received_ad = counter

        if isdir("cache") and isfile("cache/received_ad.txt"):
            with open("cache/received_ad.txt", "w") as file:
                file.write(str(counter))
        else:
            if not isdir("cache"):
                mkdir("cache")

            with open("cache/received_ad.txt", "w+") as file:
                file.write(str(counter))
        file.close()

    except (MessageNotModified, BotBlocked, InvalidQueryID): pass
    except Exception as e:
        logger.exception(e)