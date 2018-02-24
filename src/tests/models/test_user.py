import unittest
import sure

from models.user import User

class TestUser(unittest.TestCase):
    def test_for_default_properties(self):
        user = User(1, "Matheus", "Sampaio", rating=3.0)

        user.uid.should.be.equal(1)
        user.first_name.should.be.equal("Matheus")
        user.last_name.should.be.equal("Sampaio")

        user.rating.should.be.equal(3.00)
        user.is_admin.should_not.be.true
        user.is_subscriber.should_not.be.true

    def test_comparator_not_equal(self):
        greater = User(1, "Matheus", "Sampaio")
        lower = User(2, "Matheus", "Sampaio")

        (lower == greater).should_not.be.true

    def test_comparator_equal(self):
        greater = User(1, "Matheus", "Sampaio")
        lower = User(1, "Matheus", "Sampaio")

        (lower == greater).should.be.true

    def test_str(self):
        user = User(1, "Matheus", "Sampaio")

        str(user).should.be.equal("Matheus Sampaio")

    def test_create_user_without_last_name(self):
        user = User(1, "Matheus")

        user.last_name.should.be.equal("")
