import logging
import time

logger = logging.getLogger(__name__)

class User:
    SHORT_NAME_LENGTH = 15

    def __init__(self, uid, first_name, last_name="", rating=3.00, is_admin=False, is_subscriber=False, last_seen=None, created_at=None, *args, **kwargs):
        self.uid = uid
        self.first_name = first_name.title()
        self.last_name = last_name.title()

        # Optionals
        self.rating = rating
        self.is_admin = is_admin
        self.is_subscriber = is_subscriber
        self.last_seen = last_seen or time.time()
        self.created_at = created_at or time.time()


    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name).strip()

    @property
    def short_name(self):
        short_name = self.full_name

        if len(short_name) > User.SHORT_NAME_LENGTH:
            return short_name[:User.SHORT_NAME_LENGTH - 3] + "..."

        return short_name

    @property
    def is_guest(self):
        return not self.is_subscriber

    def serialize(self):
        return {
            "uid": self.uid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "rating": self.rating,
            "is_admin": self.is_admin,
            "is_subscriber": self.is_subscriber,
            "last_seen": int(self.last_seen),
            "created_at": int(self.created_at)
        }

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return "{} uid={} first_name={} last_name={} rating={} is_admin={} is_subscriber={} last_seen={}created_at={}".format(self.__class__, self.uid, self.first_name, self.last_name, self.rating, self.is_admin, self.is_subscriber, self.last_seen, self.created_at)

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.uid == other.uid:
            return True

        return False
