from asyncio import sleep, Queue
from objects import globals, QueueItem
from aiogram.utils.exceptions import MessageNotModified, BotBlocked, InvalidQueryID

current_queue = Queue()
current_spam_queue = Queue()

async def get_part() -> list:
    items: list = []

    if globals.is_mass_sending:
        for index in range(17):
            if not current_queue.empty():
                items.append(await current_queue.get())

        for index in range(10):
            if not current_spam_queue.empty():
                items.append(await current_spam_queue.get())
    else:
        for index in range(27):
            if not current_queue.empty():
                items.append(await current_queue.get())

    return items


async def send_part():
    while True:
        try:
            print(f"Current queue state is: {current_queue.qsize()} | Spam queue: {current_spam_queue.qsize()}")
            if not current_queue.empty():
                items: list = await get_part()

                for item in items:
                    try:
                        if item.is_spam: globals.current_ad_sent += 1

                        if item.message_type == QueueItem.MessageType.Audio:
                            await globals.bot.send_audio(item.chat_id, item.input_file, caption=item.caption, title=item.title, reply_markup=item.reply_markup)
                        elif item.message_type == QueueItem.MessageType.Regular:
                            await globals.bot.send_message(item.chat_id, item.text, reply_markup=item.reply_markup)
                        elif item.message_type == QueueItem.MessageType.Document:
                            await globals.bot.send_message(item.chat_id, item.input_file)
                    except Exception as send_ex:
                        if item.is_spam: globals.current_ad_cant_sent += 1
                        print(send_ex)

                if current_spam_queue.empty():
                    globals.is_mass_sending = False
        except (MessageNotModified, BotBlocked, InvalidQueryID): pass
        except Exception as e:
            print(e)

        await sleep(1)
