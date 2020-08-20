from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ VIP status and user config for UI  """

    class Meta:
        permissions = [
            ("creator", "Can create projects and invite"),
            ("admin", "Can manage projects where invited"),
            ("translator", "Can translate files from projects where invited"),
        ]

    vip_status = models.BooleanField(default=False)
    config = models.JSONField(null=True)
