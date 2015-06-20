from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    logged_in = models.BooleanField(default=False)


def login_user(sender, request, user, **kwargs):
    user.logged_in = True
    user.save()


def logout_user(sender, request, user, **kwargs):
    user.logged_in = False
    user.save()

user_logged_in.connect(login_user)
user_logged_out.connect(logout_user)
