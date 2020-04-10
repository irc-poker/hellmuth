from .base_command import BaseCommand
from .raising import Raise

class Pot(BaseCommand):
    def run(self, table, player, seat):
        bet = table.current_bet - player.action
        player.intent = Raise(table.pot + bet)

