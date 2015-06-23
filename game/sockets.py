import redis

from django.conf import settings

from gevent.greenlet import Greenlet
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.sdjango import namespace


@namespace('/game')
class GameNamespace(BaseNamespace, BroadcastMixin):

    online_users = {}

    def listener(self, channel):
        red = redis.StrictRedis(settings.REDIS_HOST).pubsub()
        red.subscribe(channel)

        while True:
            for message in red.listen():
                if isinstance(message['data'], str):
                    message = eval(message['data'])
                    self.emit(message[0], message[1:])
                else:
                    self.emit('message', message)

    def on_connect(self, user_pk, username):
        if user_pk not in self.online_users:
            self.online_users[user_pk] = username
            self.broadcast_event('change_user_list', self.online_users)
        Greenlet.spawn(self.listener, user_pk)
        return True

    def on_disconnect(self, user_pk):
        self.online_users.pop(user_pk, None)
        self.broadcast_event('change_user_list', self.online_users)
        return True
