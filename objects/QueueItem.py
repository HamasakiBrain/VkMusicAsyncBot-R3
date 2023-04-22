from aiogram.types import InputFile, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import Union

class MessageType:
    Regular = 0
    Audio = 1,
    Document = 2

class QueueItem:
    message_type: MessageType
    chat_id: int
    text: str
    reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup]
    is_spam: bool

    input_file: InputFile
    caption: str
    title: str

    def __init__(self, message_type: MessageType, chat_id: int, text: str = None, reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup] = None, is_spam: bool = False, input_file: InputFile = None, caption: str = None, title: str = None):
        self.message_type = message_type
        self.chat_id = chat_id
        self.text = text
        self.reply_markup = reply_markup
        self.is_spam = is_spam

        self.input_file = input_file
        self.caption = caption
        self.title = title