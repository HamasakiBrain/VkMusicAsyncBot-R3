from orm import Model, Integer
from objects.globals import models

class UserAudio(Model):
    tablename = "users_audios"
    registry = models

    fields = {
        'id': Integer(primary_key=True),
        'user_id': Integer(),
        'owner_id': Integer(),
        'audio_id': Integer()
    }
