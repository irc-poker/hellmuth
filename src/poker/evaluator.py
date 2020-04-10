from poker.constants import *
from poker.utils import debug

class Evaluator:
    def __init__(self, table):
        self.table = table

    def setup_send_status(self, new_hand):
        # If at least two players do some kind of action, make sure a
        # broadcast message is sent even if the last action fails.
        if new_hand:
            self.send_status = True
        else:
            self.send_status = False

    def end_hand(self):
        self.table.dealer.end_hand()
        if self.table.playing:
            self.table.dealer.deal()

    def evaluate_action(self, player, seat):
        self.send_status = True
        intent = player.intent
        should_break = intent.run(self.table, player, seat)
        return should_break


    def run(self, new_hand = False):
        player = self.table.nextup
        seat = self.table.seats.nextup

        self.setup_send_status(new_hand)

        advance = True

        while player.intent:
            player.intent.table = self.table
            player.intent.player = player
            player.intent.should_advance = True

            action = id(player.intent)
            player.intent.run(self.table, player, seat)

            if action == id(player.intent):
                result = player.intent.should_advance
                player.intent = None
                return result

