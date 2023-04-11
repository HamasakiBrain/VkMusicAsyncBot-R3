from orm import Model, Integer, DateTime, Text, Boolean
from objects.globals import models
from datetime import datetime

class User(Model):
    tablename = "users"
    registry = models

    fields = {
        'id': Integer(primary_key=True),
        'created': DateTime(default=datetime.utcnow()),
        'ref_link': Text(max_length=1000, allow_null=True),
        'user_id': Integer(unique=True),
        'last_seen': DateTime(default=datetime.utcnow()),
        'is_banned': Boolean(default=False)
    }
