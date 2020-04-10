from .base_command import BaseCommand
from .fold import Fold
from .check import Check

def l(msg):
    print(f"[CALL] {msg}")

class Call(BaseCommand):
    def __init__(self, amount = None):
        self.amount = amount

    def shove(self, table, player, sidepots=False):
        table.pots.deposit(player.jam())
        player.last_bet = table.current_bet

        l(f"{player.nick} shoving for {player.action}. ${player.in_play} in play.")

        msg = f'{player.nick} calls ${player.stack}.  Pot is ${table.pots.main}.'

        if sidepots:
            table.pots.set()
            msg = f'{player.nick} calls ${player.stack} - side pot.  Pot is ${table.pots.main}.'

        l(f"{player.nick}'s in_play is ${player.in_play}")

        self.succeed(msg)


    def undercalled(self, table, player, amount):
        if player.stack > amount:
            l("Stack is larger than bet, folding.")
            player.intent = Fold()
        else:
            l("Bet is larger than stack, can't call. Folding.")
            self.shove(table, player)

    def call(self, table, player, bet):
        table.pots.deposit(player.pay(bet))
        l(f"{player.nick} calling for {player.action}. ${player.in_play} in play.")
        self.succeed(f'{player.nick} calls ${bet}.  Pot is ${table.pots.main}.')

    def called(self, table, player, bet, call):
        # Normal call
        player.last_bet = table.current_bet

        if bet < player.stack:
            self.call(table, player, bet)

        # All-in call
        elif bet >= player.stack:
            if bet == player.stack:
                self.shove(table, player)
            else:
                self.shove(table, player, True)

    def check_call(self, table, player, bet):
        if isinstance(bet, str) and self.amount.lower().startswith("max"):
            l("Called max, setting call amount to bet: ${bet}")
            amount = bet
        else:
            try:
                amount = int(self.amount)
            except:
                amount = bet

        if amount < bet:
            self.undercalled(table, player, amount)

        else:
            self.called(table, player, bet, amount)

    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.big_blind_acted = True

        bet = table.current_bet - player.action

        self.amount = self.amount or bet

        # call $0 == check if no bet
        if bet == 0:
            l("Effective bet is zero (bet == action), calling.")
            player.intent = Check()
        else:
            # call $0 == fold if there's a bet
            if self.amount ==  0:
                l("Called $0 against bet of ${bet}, folding.")
                player.intent = Fold()
            # regular call
            else:
                self.check_call(table, player, bet)
