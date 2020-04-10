from random import shuffle

from poker.log import logger
from poker.deck import Deck
from poker.seats import SeatTracker
from poker.sidepots import SidePots
from poker.dealer import Dealer
from poker.blinds import Blinds
from poker.evaluator import Evaluator
from poker.actions.fold import Fold

def l(msg):
    print(f"[TABLE] {msg}")

class Table:

    def __init__(self, bot):
        self.bot = bot
        self.players = []

        self.hands = 0
        self.round = 0
        self.board = []
        self.current_bet = 0
        self.minraise = 0

        self.nplyin = [0, 0, 0, 0]
        self.potsize = [0, 0, 0, 0]

        self.dealer = Dealer(self)
        self.blinds = Blinds(self)
        self.seats = SeatTracker(self)
        self.deck = Deck()
        self.pots = SidePots()
        self.shuffle_players = True

    def get(self, key, default=None):
        return self.bot.db.get_plugin_value("poker", key, default=default)

    def set(self, key, value):
        return self.bot.db.set_plugin_value("poker", key, value)

    def new_session(self):
        l(f"New session.")
        self.hands = 0

        self.seats.new_session()

        for player in self.players:
            player.new_session()

        if self.shuffle_players:
            shuffle(self.players)

    def new_hand(self):
        l(f"New hand: {self.hands + 1}.")
        self.hands += 1
        self.round = 0
        self.board = []
        self.current_bet = 0
        self.pots.reset()

        self.nplyin = [0, 0, 0, 0]
        self.potsize = [0, 0, 0, 0]

        for player in self.players:
            player.new_hand()


    def new_round(self):
        l(f"New round: {self.round + 1}.")
        self.round += 1

        for player in self.players:
            player.new_round()

        self.minraise = self.default_low_blind
        self.current_bet = 0

        for player in self.players:
            player.new_round()

    #
    # Persistent Settings
    #

    @property
    def color_enabled(self):
        return self.get("color_enabled", True)

    @color_enabled.setter
    def color_enabled(self, value):
        self.set(key, value)

    @property
    def max_buyin(self):
        return self.get("max_buyin", 1000)

    @max_buyin.setter
    def max_buyin(self, value):
        self.set(key, value)

    @property
    def max_players(self):
        return self.get("max_players", 32)

    @max_players.setter
    def max_players(self, value):
        self.set(key, value)

    @property
    def min_players(self):
        return self.get("min_players", 2)

    @min_players.setter
    def min_players(self, value):
        self.set(key, value)

    @property
    def default_low_blind(self):
        return self.get("default_low_blind", 15)

    @default_low_blind.setter
    def default_low_blind(self, value):
        self.set(key, value)

    @property
    def default_high_blind(self):
        return self.get("default_high_blind", 30)

    @default_high_blind.setter
    def default_high_blind(self, value):
        self.set(key, value)

    @property
    def bankroll_amount(self):
        return self.get("bankroll_amount", 10000)

    @bankroll_amount.setter
    def bankroll_amount(self, value):
        self.set(key, value)

    @property
    def bust_chip_price(self):
        return self.get("bust_chip_price", 15000)

    @bust_chip_price.setter
    def bust_chip_price(self, value):
        self.set(key, value)

    @property
    def minimum_raise(self):
        return self.get("minimum_raise", 2)

    @minimum_raise.setter
    def minimum_raise(self, value):
        self.set(key, value)

    @property
    def hand_number(self):
        return self.get("hand_number", 0)

    @hand_number.setter
    def hand_number(self, value):
        self.set(key, value)

    #
    # Player Properties
    #

    def player_at(self, seat):
        if seat < self.n_players:
            return self.players [seat]

    @property
    def nextup(self):
        return self.player_at(self.seats.nextup)

    @property
    def button(self):
        return self.player_at(self.seats.button)

    @property
    def bb(self):
        return self.player_at(self.seats.bb)

    @property
    def sb(self):
        return self.player_at(self.seats.sb)

    @property
    def last_bettor(self):
        return self.player_at(self.seats.last_bettor)

    @property
    def sitting_players(self):
        return list(filter(lambda p: p.is_sitting, self.players))

    @property
    def eligable_players(self):
        return list(filter(lambda p: p.eligable, self.sitting_players))

    @property
    def ineligable_players(self):
        return list(filter(lambda p: not p.eligable, self.sitting_players))

    @property
    def in_hand_players(self):
        return list(filter(lambda p: p.in_hand, self.eligable_players))

    @property
    def all_in_players(self):
        return list(filter(lambda p: p.all_in, self.in_hand_players))

    @property
    def quitting_players(self):
        return list(filter(lambda p: not p.quit, self.players))

    @property
    def players_for_round(self):
        players = []

        for offset in range(self.n_players):
            seat = (self.seats.nextup + offset) % self.n_players
            player = self.players[seat]

            if player.in_hand:
                players.append(player)

        return players

    @property
    def n_players(self):
        return len(self.players)

    @property
    def n_sitting(self):
        return len(self.sitting_players)

    @property
    def n_eligable(self):
        return len(self.eligable_players)

    @property
    def n_ineligable(self):
        return len(self.ineligable_players)

    @property
    def n_in_hand(self):
        return len(self.in_hand_players)

    @property
    def n_all_in(self):
        return len(self.all_in_players)

    @property
    def n_quitters(self):
        return len(self.quitting_players)

    @property
    def playing(self):
        return self.n_eligable > 1

    #
    # Methods
    #

    def tell(self, message, who, force=False):
        if not hasattr(who, "nick"):
            who = self.named_player(who)

        if not who.quit or force:
            self.bot.say(message, who.nick)

    def say(self, message, skip=None):
        for player in self.sitting_players:
            if not skip or player not in skip:
                self.bot.say(message, player.nick)

    def longest_nick(self, players=None):
        longest_nick = 0
        for player in players or self.players:
            nick_length = len(player.nick)
            if  nick_length > longest_nick:
                longest_nick = nick_length
        return longest_nick

    def named_player(self, nick):
        for player in self.players:
            if player.nick == nick:
                return player

    def player_position(self, player):
        for i,p in enumerate(self.players):
            if player.name == p.name:
                return i

    def buyin(self, player):
        player = self.named_player(player.nick)
        chips = min(self.max_buyin, player.bankroll)
        player.bankroll -= chips
        player.stack += chips
        player.intent = None
        player.folded = True
        player.busted = False
        player.all_in = False
        l(f"{player.nick} bought in for ${player.stack}.")
        self.say(f"{player.nick} buys in with ${player.stack}, making {self.n_players} players.")

    def add_player(self, player):
        player.table = self
        player.stack = 0
        player.intent = None
        player.folded = True
        player.busted = True
        player.all_in = False
        player.quit = False

        self.players.append(player)
        l(f"{player.nick} added to the table.")
        self.say(f"{player.nick} has sat at the table.")

    def remove_player(self, player):
        player = self.named_player(player.nick)

        if player is None:
            return

        returned_chips = max(0, player.stack)
        l(f"Returning {returned_chips} to {player.nick}.")
        if returned_chips > 0:
            self.tell(f"{returned_chips} chips were returned to your bankroll.", player, True)
        player.bankroll += returned_chips
        self.players.remove(player)
        self.say(f"{player.nick} quit.")
