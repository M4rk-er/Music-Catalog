from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        'Имя пользователя',
        max_length=100,
        unique=True
    )
    email = models.EmailField(
        'Почта',
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=50
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=50
    )

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username
