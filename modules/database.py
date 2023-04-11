from db_models.User import User
from db_models.Audio import Audio
from db_models.UserAudio import UserAudio
from db_models.AudioDownloads import AudioDownloads
from objects import globals
from datetime import datetime, timedelta
from sqlite3 import IntegrityError
import time

# async def create_user(user_id: int, ref_link: str = None):
#     start_time = time.time()
#     try:
#         if user_id in globals.users_ids:
#             user = await User.objects.get(user_id=user_id)
#             await user.update(last_seen=datetime.utcnow(), is_banned=False)
#
#             for cached_user in globals.cached_users:
#                 if cached_user["user_id"] == user_id:
#                     cached_user["last_seen"] = datetime.utcnow()
#                     cached_user["is_banned"] = False
#                     return
#             return
#         else:
#             created_user = await User.objects.create(user_id=user_id, created=datetime.utcnow(), last_seen=datetime.utcnow(), ref_link=ref_link, is_banned=False)
#             globals.users_ids.append(user_id)
#             globals.cached_users.append({"user_id": created_user.user_id, "created": created_user.created, "last_seen": created_user.last_seen})
#
#             return
#
#         if user_id not in [u["user_id"] for u in globals.cached_users]:
#             if await User.objects.filter(user_id=user_id).count() == 0:
#                 created_user = await User.objects.create(user_id=user_id, created=datetime.utcnow(), last_seen=datetime.utcnow(), ref_link=ref_link, is_banned=False)
#                 globals.cached_users.append({"user_id": created_user.user_id, "created": created_user.created, "last_seen": created_user.last_seen})
#         else:
#             user = await User.objects.get(user_id=user_id)
#             await user.update(last_seen=datetime.utcnow(), is_banned=False)
#
#             for cached_user in globals.cached_users:
#                 if cached_user["user_id"] == user_id:
#                     cached_user["last_seen"] = datetime.utcnow()
#                     cached_user["is_banned"] = False
#                     return
#     except IntegrityError: pass
#     finally: globals.logger.info(f"-> create_user execution time: {time.time() - start_time}")

async def create_audio(owner_id: int, audio_id: int, artist: str, title: str, duration: int):
    store_id: str = f"{owner_id}_{audio_id}"

    if store_id not in globals.cached_audio:
        await Audio.objects.create(owner_id=owner_id, audio_id=audio_id, artist=artist, title=title, duration=duration)
        globals.cached_audio[f"{owner_id}_{audio_id}"] = {
            "owner_id": owner_id,
            "audio_id": audio_id,

            "artist": artist,
            "title": title,
            "duration": duration
        }
    else: return

async def get_users_ids():
    return [user.user_id for user in await User.objects.all()]

async def add_downloaded_audio(owner_id: int, audio_id: int):
    await AudioDownloads.objects.create(owner_id=owner_id, audio_id=audio_id, created=datetime.utcnow())

async def total_downloads():
    return await AudioDownloads.objects.count()

async def last_day_downloads():
    return await AudioDownloads.objects.filter(created__gt=(datetime.utcnow() - timedelta(days=1))).count()

async def get_audio(owner_id: int, audio_id: int):
    audios = await Audio.objects.filter(owner_id=owner_id, audio_id=audio_id).all()

    if len(audios) == 0: return None
    else: return audios[0]

# async def user_has_audio(user_id: int, owner_id: int, audio_id: int):
#     count = await UserAudio.objects.filter(user_id=user_id, owner_id=owner_id, audio_id=audio_id).count()
#     if count == 0:
#         return False
#     else:
#         return True
#
# async def user_get_audios(user_id: int):
#     return await UserAudio.objects.filter(user_id=user_id).all()
#
# async def user_add_audio(user_id: int, owner_id: int, audio_id: int):
#     await UserAudio.objects.create(user_id=user_id, owner_id=owner_id, audio_id=audio_id)
#
# async def user_remove_audio(user_id: int, owner_id: int, audio_id: int):
#     audio = await UserAudio.objects.get(user_id=user_id, owner_id=owner_id, audio_id=audio_id)
#     await audio.delete()

async def last_day_users():
    return await User.objects.filter(last_seen__gt=(datetime.utcnow() - timedelta(days=1))).count()

async def last_day_new_users():
    return await User.objects.filter(created__gt=(datetime.utcnow() - timedelta(days=1))).count()

async def get_refs():
    refs: dict = {}

    for user in await User.objects.all():
        if user.ref_link is None:
            continue

        if user.ref_link not in refs: refs[user.ref_link] = 1
        else: refs[user.ref_link] += 1

    return refs

async def remove_ref(key: str):
    users = await User.objects.filter(ref_link=key)
    for user in users:
        await user.update(ref_link=None)

async def clear_refs():
    users = await User.objects.all()
    for user in users:
        if user.ref_link is not None:
            await user.update(ref_link=None)

async def set_banned(users_ids: list):
    await globals.database.execute(f"UPDATE users SET is_banned=1 WHERE user_id IN ({', '.join([str(uid) for uid in users_ids])})")

async def get_not_banned():
    return await User.objects.filter(is_banned=False).all()

async def dev_users_count():
    return await User.objects.count()