from orm import Model, Integer, DateTime
from objects.globals import models
from datetime import datetime

class AudioDownloads(Model):
    tablename = "audio_downloads"
    registry = models

    fields = {
        'id': Integer(primary_key=True),
        'created': DateTime(default=datetime.utcnow()),
        'owner_id': Integer(),
        'audio_id': Integer()
    }
