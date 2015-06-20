from django.db import models
from django.utils.translation import ugettext_lazy as _

from users.models import User


class Game(models.Model):

    first_user = models.ForeignKey(User, verbose_name=_(u'first user'),
                                   related_name='first_user_games')
    second_user = models.ForeignKey(User, blank=True, null=True, verbose_name=_(u'second user'),
                                    related_name='second_user_games')

    class Meta:
        verbose_name = _(u'game')
        verbose_name_plural = _(u'games')

    def __unicode__(self):
        return u'game {0}'.format(self.pk)


class Move(models.Model):

    game = models.ForeignKey(Game, verbose_name=_(u'game'))
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    move = models.IntegerField(_(u'move'))

    class Meta:
        verbose_name = _(u'game move')
        verbose_name_plural = _(u'game moves')

    def __unicode__(self):
        return u'{0}: {1} - {2}'.format(self.game, self.user, self.move)
