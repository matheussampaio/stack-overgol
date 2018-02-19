import time
from functools import total_ordering


@total_ordering
class ListItem:
    def __init__(self, user, is_goalkeeper=False, is_guest=False, timestamp=False, hide_guest_label=False, hide_subscriber_label=False):
        self._user = user
        self._is_goalkeeper = is_goalkeeper
        self._is_guest = is_guest
        self._hide_guest_label = hide_guest_label
        self._hide_subscriber_label = hide_subscriber_label

        if timestamp:
            self._timestamp = timestamp
        else:
            self._timestamp = int(time.time())

    @property
    def user(self):
        return self._user

    @property
    def is_goalkeeper(self):
        return self._is_goalkeeper

    @property
    def is_guest(self):
        return self._is_guest

    @property
    def timestamp(self):
        return self._timestamp

    def serialize(self):
        return {
            "timestamp": self.timestamp,
            "is_goalkeeper": self.is_goalkeeper,
            "is_guest": self.is_guest,
            "user": self.user.serialize()
        }

    def __lt__(self, other):
        if self.is_goalkeeper != other.is_goalkeeper:
            return self.is_goalkeeper

        if self.user.is_subscriber != other.user.is_subscriber:
            return self.user.is_subscriber

        return self.timestamp < other.timestamp

    def __str__(self):
        if self.user.is_subscriber and not self._hide_subscriber_label:
            return "{} (M)".format(str(self.user))

        if not self.user.is_subscriber and not self._hide_guest_label:
            return "{} (C)".format(str(self.user))

        return str(self.user)

    def __repr__(self):
        return "{} is_goalkeeper={} is_guest={} timestamp={}".format(self.__class__, self.is_goalkeeper, self.is_guest,
                self.timestamp)
