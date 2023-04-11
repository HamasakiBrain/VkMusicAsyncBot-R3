from aiohttp import ClientSession
import json
from typing import Union

class MusicAPI:
    url: str = None
    key: str = None
    app_id: int = None

    def __init__(self, url: str, key: str, app_id: int):
        self.url = url
        self.key = key
        self.app_id = app_id

    async def get_audio(self, owner_id: int, audio_id: int):
        async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
            async with session.get(f"http://{self.url}/api.php", params={ "key": self.key, "method": "get.audio", "ids": f"{owner_id}_{audio_id}" }) as response:
                return json.loads((await response.read()).decode("utf8"))

    async def search(self, query: str):
        async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
            async with session.get(f"http://{self.url}/api.php", params={ "key": self.key, "method": "search", "q": query }) as response:
                return json.loads((await response.read()).decode("utf8"))

    async def by_owner(self, owner_id: Union[int, str]):
        async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
            async with session.get(f"http://{self.url}/api.php", params={ "key": self.key, "method": "by_owner", "owner_id": owner_id }) as response:
                return json.loads((await response.read()).decode("utf8"))

    async def chart(self):
        async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
            async with session.get(f"http://{self.url}/api.php", params={"key": self.key, "method": "chart"}) as response:
                return json.loads((await response.read()).decode("utf8"))

    async def new_songs(self):
        async with ClientSession(skip_auto_headers=["User-Agent"]) as session:
            async with session.get(f"http://{self.url}/api.php", params={"key": self.key, "method": "new_songs"}) as response:
                strdata = (await response.read()).decode("utf8")
                return json.loads(strdata)