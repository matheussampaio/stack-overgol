import time

class ListItem:
    def __init__(self, user, is_goalkeeper=False, is_guest=False, timestamp=False):
        self._user = user
        self._is_goalkeeper = is_goalkeeper
        self._is_guest = is_guest

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
        # if self.is_goalkeeper != other.is_goalkeeper:
        #     return not self.is_goalkeeper

        if self.is_guest != other.is_guest:
            return self.is_guest

        return self.timestamp > other.timestamp

    def __str__(self):
        if self.is_guest:
            return "{} (C)".format(str(self.user))

        return str(self.user)

    def __repr__(self):
        return repr(self.user)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.user == other.user

        return self.user == other
