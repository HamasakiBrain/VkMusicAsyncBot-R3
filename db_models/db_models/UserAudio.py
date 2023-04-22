from orm import Model, Integer, ModelRegistry
from objects.globals import database, metadata

class UserAudio(Model):
    tablename = "users_audios"
    registry = ModelRegistry(database)

    fields = {
        'id': Integer(primary_key=True),

        'user_id': Integer(),

        'owner_id': Integer(),
        'audio_id': Integer()
    }
