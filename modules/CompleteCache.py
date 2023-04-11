from aiogram.types import Message
from datetime import datetime
from db_models.User import User
from db_models.UserAudio import UserAudio

class CompleteCache:
    users_ids: list = []
    user_audios: dict = {}
    user_messages: dict = {}

    users: list = []

    async def load(self):
        self.users = await User.objects.all()
        for user in self.users:
            self.users_ids.append(user.user_id)

        for ua in await UserAudio.objects.all():
            if ua.user_id not in self.user_audios:
                self.user_audios[ua.user_id] = []
            self.user_audios[ua.user_id].append(ua)

    async def create_user(self, user_id: int, ref_link: str = None):
        if user_id in self.users_ids:
            for user in self.users:
                if user.user_id == user_id:
                    user.last_seen = datetime.utcnow()
                    user.is_banned = False
                    break

            user = await User.objects.get(user_id=user_id)
            await user.update(last_seen=datetime.utcnow(), is_banned=False)
        else:
            self.users_ids.append(user_id)
            await User.objects.create(user_id=user_id, created=datetime.utcnow(), last_seen=datetime.utcnow(), ref_link=ref_link, is_banned=False)

    async def user_has_audio(self, user_id: int, owner_id: int, audio_id: int):
        if user_id not in self.user_audios: return False
        for ua in self.user_audios[user_id]:
            if ua.owner_id == owner_id and ua.audio_id == audio_id: return True
        return False

    async def user_get_audios(self, user_id: int):
        if user_id not in self.user_audios: return []
        return self.user_audios[user_id]

    async def user_add_audio(self, user_id: int, owner_id: int, audio_id: int):
        if user_id not in self.user_audios: self.user_audios[user_id] = []
        self.user_audios[user_id].append(await UserAudio.objects.create(user_id=user_id, owner_id=owner_id, audio_id=audio_id))

    async def user_remove_audio(self, user_id: int, owner_id: int, audio_id: int):
        if user_id not in self.user_audios: return
        for index, ua in enumerate(self.user_audios[user_id]):
            if ua.owner_id == owner_id and ua.audio_id == audio_id:
                self.user_audios[user_id].pop(index)
                break

        audio = await UserAudio.objects.get(user_id=user_id, owner_id=owner_id, audio_id=audio_id)
        await audio.delete()

    def user_set_message(self, user_id: int, message_id: int):
        self.user_messages[user_id] = message_id

    def user_get_message(self, user_id: int):
        if user_id in self.user_messages: return self.user_messages[user_id]
        else: return None

    async def answer(self, message: Message, text: str, reply_markup, prevent_edit: bool = False):
        last_message_id: int = self.user_get_message(message.from_user.id)
        if last_message_id is None:
            answer_message = await message.answer(text, reply_markup=reply_markup, reply=True)
            self.user_set_message(message.from_user.id, answer_message.message_id)
        else:
            await message.bot.edit_message_text(text, message.chat.id, last_message_id, reply_markup=reply_markup)
        # if prevent_edit is True or last_message_id is None:
        #     answer_message: Message = await message.answer(text, reply_markup=reply_markup, reply=True)
        #     self.user_set_message(message.from_user.id, answer_message.message_id)
        # else:
        #     await message.bot.edit_message_text(text, message.chat.id, last_message_id, reply_markup=reply_markup)