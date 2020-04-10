from .base_command import BaseCommand
from .call import Call
from .raising import Raise

def l(msg):
    print(f"[BET] {msg}")

class Bet(BaseCommand):
    def __init__(self, amount):
        self.amount = int(amount)

    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.big_blind_acted = True

        bet = table.current_bet - player.action

        if self.amount < bet:
            l(f"{player.nick} tries to bet ${self.amount} under min of ${bet}")
            msg = f'Insufficient bet: minimum to call is ${bet}'
            self.fail(msg)
        elif self.amount == bet or bet > player.stack:
            l(f"{player.nick} tries to equal bet of ${self.amount} for call")
            player.intent = Call(self.amount)
        elif self.amount > bet:
            l(f"{player.nick} raises to ${self.amount}")
            l(f"amount({self.amount}) - bet({bet}) - action({player.action}) = {self.amount - bet - player.action}")
            player.intent = Raise(self.amount - bet - player.action)
