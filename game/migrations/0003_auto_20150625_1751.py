# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_remove_invite_is_active'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='invite',
            unique_together=set([('inviter', 'invitee')]),
        ),
    ]
