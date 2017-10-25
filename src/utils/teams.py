import copy
import random
import logging

from utils import configs
from models.user import User
from database.firebase import database

logger = logging.getLogger(__name__)

class Teams:
    def __init__(self):
        self.max_teams = configs.get("RACHA.MAX_TEAMS")
        self.max_players_per_team = configs.get("RACHA.MAX_NUMBER_PLAYERS_TEAM")
        self.max_players = self.max_teams * self.max_players_per_team

        self.all_colors = configs.get("RACHA.TEAMS_COLORS")
        self.range_variation = configs.get("RACHA.RATING_RANGE_VARIATION")

        self.teams = {}

    def complete_players(self, players):
        """
            Adiciona jogadores até completar os times
        """

        # Add players until we got [2, MAX_TEAMS] completed teams
        while len(players) < 2 * self.max_players_per_team or \
            (len(players) < self.max_players and len(players) % self.max_players_per_team != 0):

            user = User(None, "* Jogador", str(len(players) + 1), rating=3.00)

            players.append(user)

        return players


    def add_variation_to_players(self, players):
        """
            Adiciona uma variação nos ratings para os times não ficarem sempre iguais
        """

        for player in players:
            variation = random.uniform(self.range_variation[0], self.range_variation[1])

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


    def calculate_teams(self, all_players):
        """ Calcula os times """
        players = copy.deepcopy((all_players[:self.max_players]))

        players = self.complete_players(players)
        players = self.add_variation_to_players(players)
        players = self.sort_players(players)

        # Cria arrays para cada time
        length = int(len(players) / self.max_players_per_team)

        teams = [[] for _ in range(length)]

        # Enquanto houver jogador não alocado
        while players:
            # Coloca o melhor jogador no time mais fraco
            self.get_weakest_team(teams).append(players.pop())

        # Mistura os times finais para varias as cores dos jogadores
        random.shuffle(teams)

        self.teams = {}

        colors = self.all_colors[:len(teams)]

        for color, team in zip(colors, teams):
            self.teams[color] = [user for user in team]


    def serialize(self):
        teams = {}

        for color, team in self.teams.items():
            teams[color] = [user.serialize() for user in team]

        return teams


    def __str__(self):
        """ String representando os times """
        output = [
            "```text",
        ]

        colors = list(self.teams.keys())

        if len(colors) == 2:
            output.append("Ordem dos jogos:\n 1. {} x {}".format( \
                colors[0], colors[1]))
        elif len(colors) == 3:
            output.append("Ordem dos jogos:\n 1. {} x {}\n 2. {}\n".format( \
                colors[0], colors[1], colors[2]))
        else:
            output.append("Ordem dos jogos:\n 1. {} x {}\n 2. {}\n 3. {}\n".format( \
                colors[0], colors[1], colors[2], colors[3]))

        for color, team in self.teams.items():
            output.append("Time {}:".format(color))

            for player in team:
                name = str(player).strip()

                if len(name) > 15:
                    name = name[:12] + "..."

                output.append(" - {!s:<15} ({:.1f})".format(name, player.rating))

            output.append("")

        output.append("```")

        return "\n".join(output)
