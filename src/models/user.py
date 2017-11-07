import logging

logger = logging.getLogger(__name__)

class User:
    def __init__(self, uid, first_name, last_name="", rating=3.00, is_admin=False, is_subscriber=False, *args, **kwargs):
        self._uid = uid
        self._first_name = first_name
        self._last_name = last_name

        # Optionals
        self._rating = rating
        self._is_admin = is_admin
        self._is_subscriber = is_subscriber

    @property
    def uid(self):
        return self._uid

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        self._rating = value

    @property
    def is_admin(self):
        return self._is_admin

    @property
    def is_subscriber(self):
        return self._is_subscriber

    def serialize(self):
        return {
            "uid": self.uid,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "rating": self.rating,
            "is_admin": self.is_admin,
            "is_subscriber": self.is_subscriber
        }

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def __repr__(self):
        return "{} uid={} first_name={} last_name={} rating={} is_admin={} is_subscriber={}".format(self.__class__, self.uid, self.first_name, self.last_name, self.rating, self.is_admin, self.is_subscriber)

    def __eq__(self, other):
        logger.info('qs {} {}'.format(str(self), str(other)))
        logger.info(isinstance(other, self.__class__))
        logger.info(self.uid == other.uid)
        if isinstance(other, self.__class__) and self.uid == other.uid:
            return True

        return False
