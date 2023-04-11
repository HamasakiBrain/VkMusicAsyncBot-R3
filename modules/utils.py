import random
import hashlib
import datetime
from pytz import timezone
from urllib import parse
from objects import globals

def random_string(length: int, characters: str):
    return ''.join(random.choice(characters) for _ in range(length))

def convert_from_seconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    if hour == 0:
        return "%02d:%02d" % (minutes, seconds)
    else:
        return "%d:%02d:%02d" % (hour, minutes, seconds)

def get_audio_url(owner_id: int, audio_id: int, artist: str, title: str):
    track_name = parse.quote_plus(f"{artist}-{title}")

    hour = str(datetime.datetime.now(timezone("Europe/Moscow")).hour)
    if hour == "24": hour = "00"
    if len(hour) == 1: hour = f"0{hour}"

    encode_me: str = f"{globals.current_ip}_{globals.config['api_key']}_{owner_id}_{audio_id}_{hour}"

    m = hashlib.md5()
    m.update(encode_me.encode())
    vk_hash = m.hexdigest()

    return f"http://{globals.config['api_url']}/download_{owner_id}_{audio_id}_{globals.config['api_app_id']}_{vk_hash}/{track_name}.mp3"

def paginate(data_list: list, count: int):
    for i in range(0, len(data_list), count):
        yield data_list[i:i + count]
