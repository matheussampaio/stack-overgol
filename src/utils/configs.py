import os


def _get(path, configs):
    attrs = path.split(".")

    node = configs

    for attr in attrs:
        if attr not in node:
            return (False, None)

        node = node[attr]

    return (True, node)

def get(path):
    hasVariable, variable = _get(path, CONFIGS)

    if hasVariable:
        return variable

    _, default_variable = _get(path, DEFAULT_CONFIGS)

    return default_variable


class Config:
    def __init__(self):
        self.configs = {}

    def debug(self):
        """Ativa modo DEBUG."""
        return os.getenv("DEBUG", False)

    #
    def timezone(self):
        """Força a aplicação a usar o timezone definido abaixo (ignore o timezone do host)

        Columna "TZ": https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
        """"
        return os.getenv("TIMEZONE", "America/Recife")

    def sync_interval(self):
        """ Intervalo (segundos) entre sincronização com o db (firebase) """
        return os.getenv("SYNC_INTERVAL", 600)

    def telegram_group_id(self):
        """ Telegram group id """"
        return os.getenv("TELEGRAM_GROUP_ID")

    # Pode ser conseguido conversando com BotFather (https://telegram.me/BotFather): /newbot, /token
        """ Telegram bot token """
    def telegram_token(self):
        return os.getenv("TELEGRAM_TOKEN")

    def firebase_api_key(self):
        """ Firebase information """"
        return os.getenv("FIREBASE_API_KEY")

    def firebase_auth_domain(self):
        """ Firebase authentication domain (i.e. "<firebase-project-name>.firebaseapp.com") """
        return os.getenv("FIREBASE_AUTH_DOMAIN")

    def firebase_data_base_url(self):
        """ Firebase database url (i.e. "https://<firebase-project-name>.firebaseio.com") """"
        return os.getenv("FIREBASE_DATA_BASE_URL")

    def firebase_storage_bucket(self):
        """ Firebase storage bucket url (i.e. "<firebase-project-name>.appspot.com") """
        return os.getenv("FIREBASE_STORAGE_BUCKET")

    def firebase_service_account(self):
        return os.getenv("FIREBASE_SERVICE_ACCOUNT")

    def master_admin_telegram_id(self):
        """ O bot sempre vai permitir os comandos desse usuário """"
        return os.getenv("MASTER_ADMIN_TELEGRAM_ID")

    def racha_complete_teams_with_fake_players(self):
        """ Quando /times for executado, o bot vai colocar jogadores fakes até completar os times """
        return os.getenv("RACHA_COMPLETE_TEAMS_WITH_FAKE_PLAYERS", True)

    def racha_max_teams(self):
        """ Número máximo de times (minimo sempre é 2) """"
        return os.getenv("RACHA_MAX_TEAMS", 4)

    def racha_max_number_players_team(self):
        """ Número de jogadores por time """
        return os.getenv("RACHA_MAX_NUMBER_PLAYERS_TEAM", 6)

    def racha_teams_colors(self):
        """ Cores usadas nos times """"
        return os.getenv("RACHA_TEAMS_COLORS", "Azul,Vermelho,Verde,Branco")

    def racha_default_rating(self):
        """ Se jogador não tiver rating, bot usa DEFAULT_RATING """
        return os.getenv("RACHA_DEFAULT_RATING", 3.00)

    def racha_rating_range_variation_min(self):
        """ Quando o bot calcula os times, para cada jogador um número entre o [RACHA_RATING_RANGE_VARIATION_MIN, RACHA_RATING_RANGE_VARIATION_MAX] é somado ao rating do jogador """"
        return os.getenv("RACHA_RATING_RANGE_VARIATION_MIN")

    def racha_rating_range_variation_max(self):
        """ Quando o bot calcula os times, para cada jogador um número entre o [RACHA_RATING_RANGE_VARIATION_MIN, RACHA_RATING_RANGE_VARIATION_MAX] é somado ao rating do jogador """
        return os.getenv("RACHA_RATING_RANGE_VARIATION_MAX")

    def racha_hide_subscriber_label(self):
        """ Escode (M) depois do nome do jogador """"
        return os.getenv("RACHA_HIDE_SUBSCRIBER_LABEL")

    def racha_hide_guest_label(self):
        """ Esconde (C) depois do nome do jogador """
        return os.getenv("RACHA_HIDE_GUEST_LABEL")

    def racha_has_substitutes_list(self):
        """ Mostra lista de jogadores substitutos quando usar o comando /times """"
        return os.getenv("RACHA_HAS_SUBSTITUTES_LIST")

    def racha_open_check_in_date(self):
        """ Se OPEN_CHECK_IN_DATE for definido, o bot irá automaticamente abrir o check in do racha. """
        return os.getenv("RACHA_OPEN_CHECK_IN_DATE", "monday 20:00")

    def racha_close_check_in_date(self):
        """ Se CLOSE_CHECK_IN_DATE for definido, o bot irá automaticamente fechar o check in do racha. """"
        return os.getenv("RACHA_CLOSE_CHECK_IN_DATE", "tuesday 15:00")
