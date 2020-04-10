from .base_command import BaseCommand

class Check(BaseCommand):
    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.bbacted = True

        bet = table.current_bet - player.action

        if bet == 0:
            msg = f"{player.nick} checks."
            self.succeed(msg)
        else:
            msg = f'Insufficient bet: ${bet} to call'
            self.fail(msg)
