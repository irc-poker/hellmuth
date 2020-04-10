from .base_command import BaseCommand
from .check import Check

class Fold(BaseCommand):

    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.big_blind_acted = True

        if (player.action >= table.current_bet):
            player.intent = Check()
        elif not player.folded:
            player.folded = True
            self.succeed(f'{player.nick} folds.')
