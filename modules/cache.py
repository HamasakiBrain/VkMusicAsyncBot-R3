from asyncio import sleep
from modules.utils import get_audio_url
from aiohttp import ClientSession
from io import BytesIO
from datetime import datetime

class Cache:
    chart_downloaded: bool = False
    new_songs_downloaded: bool = False

    loop = None
    logger = None
    music_api = None

    chart: list = []
    new_songs: list = []

    cooldown: int = 30

    def __init__(self, loop, logger, music_api, cooldown: int):
        self.loop = loop
        self.logger = logger
        self.music_api = music_api
        self.cooldown = cooldown

        self.loop.create_task(self.chart_refresh())
        self.loop.create_task(self.new_songs_refresh())

    async def chart_refresh(self):
        await sleep(2)
        while True:
            start_time = datetime.utcnow()
            data = await self.music_api.chart()

            _temp: list = []
            async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
                for track in data["list"]:
                    _temp.append(track)
                    # async with session.get(get_audio_url(track["owner_id"], track["audio_id"], track["artist"], track["title"])) as response:
                    #     track["audio"] = BytesIO(await response.read())
                    #     _temp.append(track)

            self.chart = _temp
            self.logger.info(f"Cached {len(data['list'])} tracks from chart ({(datetime.utcnow() - start_time).total_seconds()}s).")
            self.chart_downloaded = True
            await sleep(self.cooldown)

    async def new_songs_refresh(self):
        await sleep(2)
        while True:
            start_time = datetime.utcnow()
            data = await self.music_api.new_songs()

            _temp: list = []
            async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
                for track in data["list"]:
                    _temp.append(track)
                    # async with session.get(get_audio_url(track["owner_id"], track["audio_id"], track["artist"], track["title"])) as response:
                    #     #track["audio"] = BytesIO(await response.read())
                    #     _temp.append(track)

            self.new_songs = _temp
            self.logger.info(f"Cached {len(data['list'])} tracks from new songs ({(datetime.utcnow() - start_time).total_seconds()}s).")
            self.new_songs_downloaded = True
            await sleep(self.cooldown)

    def get_track(self, audio_id):
        for track in self.chart:
            if f"{track['owner_id']}_{track['audio_id']}" == audio_id:
                return track

        for track in self.new_songs:
            if f"{track['owner_id']}_{track['audio_id']}" == audio_id:
                return track
