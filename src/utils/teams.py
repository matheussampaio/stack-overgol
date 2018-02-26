import copy
import random
import logging

from utils import configs
from models.user import User
from database.firebase import database

logger = logging.getLogger(__name__)

class Teams:
    def __init__(self):
        self.teams = {}
        self.substitutes = []

    def complete_players(self, players, max_players, number_teams, team_size):
        """
            Adiciona jogadores até completar os times
        """

        def less_than_two_teams_complete():
            return len(players) < 2 * team_size

        def at_least_one_team_incomplete():
            return len(players) < max_players and len(players) % team_size != 0

        # Add players until we got [2, MAX_TEAMS] completed teams
        while less_than_two_teams_complete() or at_least_one_team_incomplete():
            user = User(None, "* Jogador", str(len(players) + 1), rating=3.00)

            players.append(user)

        return players


    def add_variation_to_players(self, players, rating_range_variation):
        """
            Adiciona uma variação nos ratings para os times não ficarem sempre iguais
        """

        for player in players:
            variation = random.uniform(rating_range_variation[0], rating_range_variation[1])

            player.rating += variation

        return players


    def sort_players(self, players):
        """
            Ordena os jogadores por rating
        """
        return sorted(players, key=lambda p: p.rating)


    def get_weakest_team(self, teams):
        """ Retorna o time com a menor soma de ratings """
        return min(teams, key=lambda team: sum([user.rating for user in team]))


    def get_teams_labels(self, teams, team_labels=[]):
        if len(teams) <= len(team_labels):
            return team_labels[:len(teams)]

        alphabetic = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        extra_team_labels = []

        for i in range(0, len(teams) - len(team_labels)):
            label = alphabetic[i % len(alphabetic)]

            # if starting to repeat labels, append a suffix
            # i.e.: A, A2, A3
            if i >= len(alphabetic):
                label += str(int(i / len(alphabetic)))

            extra_team_labels.append(label)

        return team_labels + extra_team_labels


    def calculate_teams(self, all_players, number_teams=2, team_size=5, teams_labels=[], rating_range_variation=False, complete_team_with_fake_players=False):
        """ Calcula os times """
        max_players = number_teams * team_size

        players = copy.deepcopy((all_players[:max_players or len(all_players)]))

        if complete_team_with_fake_players:
            players = self.complete_players(players, max_players, number_teams, team_size)

        if rating_range_variation:
            players = self.add_variation_to_players(players, rating_range_variation)

        players = self.sort_players(players)

        self.substitutes = copy.deepcopy((all_players[max_players or len(all_players):]))

        if rating_range_variation:
            self.substitutes = self.add_variation_to_players(self.substitutes, rating_range_variation)

        # if `team_size` is equal or less than 0 divide every player between `max_teams`
        if not team_size:
            length = number_teams
        # else, divide the players between the minimum (floor) of teams
        else:
            length = int(len(players) / team_size)

        # Cria arrays para cada time
        teams = [[] for _ in range(length)]

        # Enquanto houver jogador não alocado
        while players:
            # Coloca o melhor jogador no time mais fraco
            self.get_weakest_team(teams).append(players.pop())

        # Mistura os times finais para variar as cores dos jogadores
        random.shuffle(teams)

        self.teams_labels = self.get_teams_labels(teams, teams_labels)

        self.teams = {}

        for team_label, team in zip(self.teams_labels, teams):
            self.teams[team_label] = [user for user in team]

    def serialize(self):
        teams = {}

        for color, team in self.teams.items():
            teams[color] = [user.serialize() for user in team]

        return teams


    def format(self, with_substitutes=False):
        """ String representando os times """
        output = [
            "```",
            "Times",
            ""
        ]

        if len(self.teams_labels) > 2:
            output.append("Ordem dos jogos:")
            output.append(" 1. {} x {}".format(self.teams_labels[0], self.teams_labels[1]))

            for i, team_label in enumerate(self.teams_labels[2:]):
                output.append(" {}. {}".format(i + 2, team_label))

            output.append("")

        for team_label in self.teams_labels:
            team = self.teams[team_label]

            output.append("Time {}:".format(team_label))

            for i, player in enumerate(team):
                output.append("{:>2} - {!s:<{short_name_length}} ({:.1f})".format(i + 1, player.short_name, player.rating, short_name_length=User.SHORT_NAME_LENGTH))

            output.append("")

        if with_substitutes and self.substitutes:
            output.append("Reservas:")

            for i, player in enumerate(self.substitutes):
                output.append("{:>2} - {!s:<{short_name_length}} ({:.1f})".format(i + 1, player.short_name, player.rating, short_name_length=User.SHORT_NAME_LENGTH))

            output.append("")

        output.append("```")

        return "\n".join(output)
