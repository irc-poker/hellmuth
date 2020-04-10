from poker.hand import Hand
from poker.utils import cmp
from poker.actions.quit import Quit

class Player:

    def __init__(self, bot, nick):
        self.nick = nick
        self.bot = bot
        self.table = None
        self.intent = None
        self.hand = Hand()
        self.stack = 0
        self.old_stack = 0
        # how many chips we've bet
        self.in_play = 0
        self.action = 0
        # tracking
        self.last_bet = 0
        # flags
        self.folded = True
        self.busted = True
        self.quit = False
        self.all_in = False
        self.auto_fold = True

    def __eq__(self, other):
        return self.nick == other.nick

    def get(self, key, default=None):
        return self.bot.db.get_nick_value(self.nick, key, default=default)

    def set(self, key, value):
        return self.bot.db.set_nick_value(self.nick, key, value)

    def new_session(self):
        pass

    def new_hand(self):
        self.hand.muck()

        if self.intent and not isinstance(self.intent, Quit):
            self.intent = None

        self.inplay = 0
        self.action = 0

        self.old_stack = self.stack
        self.lastbet = 0

        self.folded = False
        self.allin = False

    def new_round(self):
        self.action = 0
        self.last_bet = 0

    def pay(self, value):
        if value == self.stack:
            self.all_in = True
        self.stack -= value
        self.in_play += value
        self.action += value
        self.total_action += value
        return value

    def jam(self):
        return self.pay(self.stack)

    @property
    def is_sitting(self):
        return not self.quit

    @property
    def eligable(self):
        return self.is_sitting and not self.busted

    @property
    def in_hand(self):
        return self.eligable and not self.folded

    @property
    def bankroll(self):
        return self.get("bankroll", 0)

    @bankroll.setter
    def bankroll(self, value):
        self.set("bankroll", value)

    @property
    def broke_chips(self):
        return self.get("broke_chips", 0)

    @broke_chips.setter
    def broke_chips(self, value):
        self.set("broke_chips", value)

    @property
    def total_winnings(self):
        return self.get("total_winnings", 0)

    @total_winnings.setter
    def total_winnings(self, value):
        self.set("total_winnings", value)

    @property
    def total_action(self):
        return self.get("total_action", 0)

    @total_action.setter
    def total_action(self, value):
        self.set("total_action", value)

    #Sort based on total action
    def actionsort(self, other):
        return cmp(self.inplay, other.inplay)

    # Note: This sorts in descending order
    def oldbrsort(self, other):
        log.logger.debug('Player.oldbrsort()')
        return cmp(other.oldbankroll, self.oldbankroll)

    def status_as_string(self, nick_width=None):
        nick_width = nick_width or len(self.nick)
        icon = "             "
        if self.nick == self.table.button.nick:
            icon = "Button       "
        elif self.nick == self.table.sb.nick:
            icon = "Small Blind  "
        elif self.nick == self.table.bb.nick:
            icon = "Big Blind    "
        return f"{self.nick:>{nick_width}} {icon} ${self.stack}"

    def hand_as_string(self, nick_width=None):
        nick_width = nick_width or len(self.nick)
        hand = self.hand.showhole(True)
        return f"{self.nick:>{nick_width}} ${hand}"

