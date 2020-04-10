from .base_command import BaseCommand
from .check import Check


def l(msg):
    print(f"[CALLMAX] {msg}")


class CallMax(BaseCommand):

    def shove(self, table, player, seat, bet):
        table.pots.deposit(player.jam())
        l(f"{player.nick} shoving for ${player.action}. ${player.in_play} in play.")
        table.pots.set()
        msg = f'{player.nick} calls ${player.stack} - side pot.  Pot is ${table.pots.main}.'
        self.succeed(msg)

    def call(self, table, player, seat, bet):
        table.pots.deposit(player.pay(bet))
        l(f"{player.nick} calling for ${player.action}. ${player.in_play} in play.")
        player.last_bet = table.current_bet
        msg = f'{player.nick} calls ${bet}.  Pot is ${table.pots.main}.'
        self.succeed(msg)

    def call_max(self, table, player, seat, bet):
        # All-in call
        if player.stack < bet:
            self.shove(table, player, seat, bet)
        else:
            self.call(table, player, seat, bet)

    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.big_blind_acted = True

        bet = table.current_bet - player.action

        # Call $0 == check
        if bet == 0:
            l(f"No bet. Checking.")
            player.intent = Check()
        else:
            self.call_max(table, player, seat, bet)
