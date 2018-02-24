import sure
import unittest
from copy import deepcopy

from models.user import User
from models.listitem import ListItem

class TestListItem(unittest.TestCase):
    def setUp(self):
        self.u_gk_guest = User(100, "goalkeeper", "guest", is_subscriber=False)
        self.li_gk_guest = ListItem(self.u_gk_guest, is_goalkeeper=True, is_guest=False, timestamp=100)

        self.u_gk_sub = User(101, "goalkeeper", "subscriber", is_subscriber=True)
        self.li_gk_sub = ListItem(self.u_gk_sub, is_goalkeeper=True, is_guest=False, timestamp=100)

        self.u_p_guest = User(102, "player", "guest", is_subscriber=False)
        self.li_p_guest = ListItem(self.u_p_guest, is_goalkeeper=False, is_guest=False, timestamp=100)

        self.u_p_sub = User(103, "player", "subscriber", is_subscriber=True)
        self.li_p_sub = ListItem(self.u_p_sub, is_goalkeeper=False, is_guest=False, timestamp=100)

    def test_guest_gk_before_guest_player(self):
        (self.li_gk_guest < self.li_p_guest).should.be.true

    def test_guest_gk_before_sub_player(self):
        (self.li_gk_guest < self.li_p_sub).should.be.true

    def test_sub_gk_before_guest_player(self):
        (self.li_gk_sub < self.li_p_guest).should.be.true

    def test_sub_gk_before_sub_player(self):
        (self.li_gk_sub < self.li_p_sub).should.be.true

    def test_sub_gk_before_guest_gk(self):
        (self.li_gk_sub < self.li_gk_guest).should.be.true

    def test_sub_player_before_guest_player(self):
        (self.li_p_sub < self.li_p_guest).should.be.true

    def test_firt_before_last(self):
        l_li_gk_guest = deepcopy(self.li_gk_guest)
        l_li_gk_guest._timestamp = self.li_gk_guest.timestamp + 1

        (self.li_gk_guest < l_li_gk_guest).should.be.true

    def test_guest_str_should_contains_C(self):
        (str(self.li_gk_guest)).should.be.equal("Goalkeeper Guest   (C)")

    def test_sub_str_should_contains_M(self):
        (str(self.li_gk_sub)).should.be.equal("Goalkeeper Subs... (M)")
