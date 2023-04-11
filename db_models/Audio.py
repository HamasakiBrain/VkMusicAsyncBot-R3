from orm import Model, Integer, Text
from objects.globals import models

class Audio(Model):
    tablename = "audios"
    registry = models

    fields = {
        'id': Integer(primary_key=True),
        'owner_id': Integer(),
        'audio_id': Integer(),
        'artist': Text(),
        'title': Text(),
        'duration': Integer()
    }
