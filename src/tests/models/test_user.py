import unittest
import sure

from models.user import User

class TestUser(unittest.TestCase):
    def test_for_default_properties(self):
        user = User(1, "first_name", "last_name", rating=3.0)

        user.uid.should.be.equal(1)
        user.first_name.should.be.equal("first_name")
        user.last_name.should.be.equal("last_name")

        user.rating.should.be.equal(3.00)
        user.is_admin.should_not.be.true
        user.is_subscriber.should_not.be.true

    def test_comparator_not_equal(self):
        greater = User(1, "first_name", "last_name")
        lower = User(2, "first_name", "last_name")

        (lower == greater).should_not.be.true

    def test_comparator_equal(self):
        greater = User(1, "first_name", "last_name")
        lower = User(1, "first_name", "last_name")

        (lower == greater).should.be.true

    def test_str(self):
        user = User(1, "first_name", "last_name")

        str(user).should.be.equal("first_name last_name")

    def test_create_user_without_last_name(self):
        user = User(1, "first_name")

        user.last_name.should.be.equal("")
