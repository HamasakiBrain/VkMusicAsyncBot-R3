from orm import Model, Integer, Text, ModelRegistry
from objects.globals import database, metadata

class Audio(Model):
    tablename = "audios"
    registry = ModelRegistry(database)

    fields = {
        'id': Integer(primary_key=True),

        'owner_id': Integer(),
        'audio_id': Integer(),

        'artist': Text(),
        'title': Text(),
        'duration': Integer()
    }
