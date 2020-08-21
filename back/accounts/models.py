from django.db import models
from django.contrib.auth.models import UserManager, AbstractUser


class UserProfile(AbstractUser):
    """ VIP status and user config for UI  """

    vip_status = models.BooleanField(default=False)
    config_o = models.JSONField(null=True)

    objects = UserManager()

    # class Meta:
        # 'verbose_name': 'user',
        # 'verbose_name_plural': 'users',
        # 'abstract': False,
    #     permissions = [
    #         ("creator", "Can create projects and invite"),
    #         ("admin", "Can manage projects where invited"),
    #         ("translator", "Can translate files from projects where invited"),
    #     ]

