from datetime import datetime
from functools import total_ordering

from models.user import User

@total_ordering
class ListItem:
    def __init__(self, user, is_goalkeeper=False, is_guest=False, timestamp=False, hide_guest_label=False, hide_subscriber_label=False):
        self.user = user
        self.is_goalkeeper = is_goalkeeper
        self.is_guest = is_guest
        self.timestamp = timestamp or int(datetime.utcnow().timestamp())

        self.hide_guest_label = hide_guest_label
        self.hide_subscriber_label = hide_subscriber_label

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
        if self.user.is_subscriber and not self.hide_subscriber_label:
            return "{!s:<{short_name_length}} (M)".format(self.user.short_name, short_name_length=User.SHORT_NAME_LENGTH)

        if not self.user.is_subscriber and not self.hide_guest_label:
            return "{!s:<{short_name_length}} (C)".format(self.user.short_name, short_name_length=User.SHORT_NAME_LENGTH)

        return "{!s:<{short_name_length}}".format(self.user.short_name, short_name_length=User.SHORT_NAME_LENGTH)

    def __repr__(self):
        return "{} is_goalkeeper={} is_guest={} timestamp={}".format(self.__class__, self.is_goalkeeper, self.is_guest,
                self.timestamp)
