from .base_command import BaseCommand
from .bet import Bet
from .callmax import CallMax

def l(msg):
    print(f"[JAM] {msg}")

class Jam(BaseCommand):
    def run(self, table, player, seat):
        bet = table.current_bet - player.action

        if player.stack < bet:
            l(f"{player.nick} jams via CallMax")
            player.intent = CallMax()
        else:
            l(f"{player.nick} jams bets for {player.stack + player.action}")
            player.intent = Bet(player.stack + player.action)

