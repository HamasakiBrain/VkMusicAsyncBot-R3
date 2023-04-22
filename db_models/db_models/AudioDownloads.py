from orm import Model, Integer, DateTime, ModelRegistry
from objects.globals import database, metadata
from datetime import datetime

class AudioDownloads(Model):
    tablename = "audio_downloads"
    registry = ModelRegistry(database)

    fields = {
        'id': Integer(primary_key=True),
        'created': DateTime(default=datetime.utcnow()),
        'owner_id': Integer(),
        'audio_id': Integer()
    }
