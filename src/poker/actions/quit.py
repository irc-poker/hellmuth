from .base_command import BaseCommand
from .fold import Fold


class Quit(BaseCommand):

    def run(self, table, player, seat):
        player.quit = True
        player.intent = Fold()
