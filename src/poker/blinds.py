
class Blinds:
    def __init__(self, table):
        self.table = table

    def set_small_blind(self, player, amount, all_in = False):
        self.small_blind = (player, amount, all_in)

    def set_big_blind(self, player, amount, all_in = False):
        self.big_blind = (player, amount, all_in)

    def post_small_blind(self):
        if self.table.seats.no_small_blind:
            return

        sb = self.table.sb
        stack = self.table.sb.stack
        low_blind = self.table.default_low_blind

        if stack > 0:
            if stack <= low_blind:
                self.table.pots.deposit(sb.jam())
                self.sidepots = True
                self.set_small_blind(sb, stack, True)
            else:
                self.table.pots.deposit(sb.pay(low_blind))
                self.set_small_blind(sb, low_blind, False)

    def post_big_blind(self):
        bb = self.table.bb
        stack = bb.stack
        high_blind = self.table.default_high_blind

        if stack <= high_blind:
            self.table.pots.deposit(bb.jam())
            self.table.pots.set()
            self.set_big_blind(bb, stack, True)
        else:
            self.table.pots.deposit(bb.pay(high_blind))
            self.set_big_blind(bb, high_blind, False)

        self.table.minraise = high_blind
        self.table.current_bet = high_blind
        self.table.seats.last_bettor = self.table.seats.bb

    def post(self):
        self.small_blind = None
        self.big_blind = None

        self.post_small_blind()
        self.post_big_blind()

        small_blind_msg = "No small blind."
        if self.small_blind:
            player, amount, all_in = self.small_blind
            small_blind_msg = f"{player.nick} blinds {amount}"
            small_blind_msg += " (all in)." if all_in else "."

        player, amount, all_in = self.big_blind
        big_blind_msg = f"{player.nick} blinds {amount}"
        big_blind_msg += " (all in)." if all_in else "."

        self.table.say(f"{small_blind_msg} {big_blind_msg} Pot: ${self.table.pots.main}")





