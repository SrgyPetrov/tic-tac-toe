# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_user', models.ForeignKey(related_name='first_user_games', verbose_name='first user', to=settings.AUTH_USER_MODEL)),
                ('second_user', models.ForeignKey(related_name='second_user_games', verbose_name='second user', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'game',
                'verbose_name_plural': 'games',
            },
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('move', models.IntegerField(verbose_name='move')),
                ('game', models.ForeignKey(verbose_name='game', to='game.Game')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'game move',
                'verbose_name_plural': 'game moves',
            },
        ),
    ]
