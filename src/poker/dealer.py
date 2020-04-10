from .log import logger
from .evaluator import Evaluator
from .hand import Hand
from .constants import *
from .utils import printboard, plural, debug, win_seat_sort

def l(msg):
    print(f"[DEALER] {msg}")

class Dealer:
    def __init__(self, table):
        self.table = table
        self.playing = False
        self.engine = Evaluator(table)

    def say(self, msg, skip=None):
        self.table.say(msg, skip)

    def tell(self, who, msg):
        self.table.tell(msg, who)

    def announce_roster(self):
        players = self.table.players_for_round
        longest_nick = self.table.longest_nick()

        for player in players:
            self.say(player.status_as_string(longest_nick))

    #
    # session
    #

    def start_session(self, one_hand=False):
        l(f"Starting session.")
        self.playing = True
        self.last_hand = one_hand
        self.table.new_session()
        self.start_hand()

    def end_session(self, abort = False):
        l(f"Ending session.")
        self.playing = False

        if abort:
            self.table.say("Play has been terminated by an admin.")
        else:
            last_player = self.table.eligable_players [0]
            self.table.bot.say("You are the only remaining player.", last_player.nick)

        hands = self.table.hands
        pluralized = plural("hand", hands)
        self.table.say(f"Play has ended after {hands} {pluralized}.")

    #
    # hands
    #

    def start_hand(self):
        l("Starting new hand.")
        self.table.new_hand()

        self.check_quitters()
        if not self.table.playing:
            self.end_hand()
            return

        self.announce_roster()
        self.table.blinds.post()
        self.table.board = self.deal_cards(self.table.deck,
                                           self.table.eligable_players,
                                           self.table.seats.button)
        self.wait_for_action(True)

    def end_hand(self, showdown = True):
        l(f"Ending hand.")
        self.showdown()
        self.check_busted_players()
        self.check_quitters()

        if not self.table.playing:
            self.end_session()
            return

        if not self.last_hand:
            self.table.seats.advance_button()
            self.start_hand()

    #
    # dealing
    #

    def deal_cards(self, deck, players, button):
        l(f"Dealing cards.")
        n_players = self.table.n_players

        deck.shuffle()

        position = 1
        for n in range(2):
            for p in range(n_players):
                player = players[(button + 1 + p) % n_players]
                if not player.busted:
                    acard = deck.nextcard()
                    player.hand.addcard(acard)
                    player.hand.seat = players.index(player)
                    if n == 0:
                        player.position = position
                        position += 1

        board = []
        for n in range(5):
            acard = deck.nextcard()
            board.append(acard)

        return board

    def flipcards(self):
        table = self.table
        round = table.round
        board = table.board
        pot = table.pots.main
        n_in_hand = table.n_in_hand

        buf = ''
        if round == PREFLOP:
            l(f"Flipping flop... {board[0].face()} {board[1].face()} {board[2].face()}")
            buf += 'Flop : '
            for i in range(3):
                buf += board[i].face(True) + ' '
            table.potsize[FLOP-1] = pot
            table.nplyin[FLOP-1] = n_in_hand
        elif round == FLOP:
            l(f"Flipping turn... {board[3].face()}")
            buf += 'Turn : '
            buf += board[3].face(True) + ' '
            table.potsize[TURN-1] = pot
            table.nplyin[TURN-1] = n_in_hand
        elif round == TURN:
            l(f"Flipping river... {board[4].face()}")
            buf += 'River: '
            buf += board[4].face(True) + ' '
            table.potsize[RIVER-1] = pot
            table.nplyin[RIVER-1] = n_in_hand

        table.say(f'Board:      {printboard(table)} (${table.pots.main})')

    def flipout(self):
        l(f"Flipping out")
        while self.table.round < RIVER:
            self.table.round += 1
            self.flipcards()

        self.end_hand()

    def announce_player_counts(self):
        n_in_hand = self.table.n_in_hand
        n_all_in = self.table.n_all_in

        buf = ''
        buf += '%d players' % n_in_hand
        if n_all_in:
            buf += ', %d all in' % n_all_in

        self.table.say(buf)

    def select_first_bettor(self):
        l(f"Selecting first bettor")
        goodbettor = False
        seats = self.table.seats
        seats.last_bettor = seats.button
        while not goodbettor:
            seats.last_bettor = seats.after(seats.last_bettor)
            goodbettor = not self.table.players[seats.last_bettor].all_in

        seats.nextup = seats.last_bettor

    def start_round(self):
        self.check_quitters()
        if not self.table.playing or self.table.n_in_hand < 2:
            self.end_hand()
            return

        # end the hand if we already did the river
        if self.table.round == RIVER:
            self.end_hand()
            return

        l(f"Starting new round")
        if not self.table.playing:
            self.flipout()
            return

        # flipout if everyone is all in
        if self.table.n_in_hand - self.table.n_all_in <= 1:
            self.flipout()
            return

        # reset round action
        self.table.new_round()

        # flip board cards for current round
        self.flipcards()

        # Find the first player to the left of the button who's not all in
        self.select_first_bettor()
        self.wait_for_action()
    #
    # end hand
    #

    def check_busted_players(self):
        busted = []
        for player in self.table.players:
            if not player.busted and player.stack == 0:
                l(f"{player.nick} busted.")
                self.table.say('%s is busted!' % player.nick)
                player.busted = True
                player.all_in = False
                player.action = 0
                player.in_play = 0

    def check_quitters(self):
        removed = []
        for player in self.table.players:
            if player.quit:
                l(f"{player.nick} quit.")
                removed.append(player)

        for player in removed:
            self.table.remove_player(player)

        return self.table.playing

    #
    # action evaluation
    #
    def wait_for_action(self, showall=False):
        self.check_quitters()
        if not self.table.playing or self.table.n_in_hand < 2:
            self.end_hand()
            return

        nextup = self.table.nextup

        if nextup.intent is not None:
            self.act()
            return

        l(f"Waiting for {self.table.nextup.nick} to act.")
        next_nick = nextup.nick
        bet = self.table.current_bet - nextup.action
        self.table.tell(f"Your cards: {nextup.hand.showhole(True)}", nextup)
        self.table.tell(f"It's your turn. ${bet} to call.", nextup)

        if showall:
            for player in self.table.in_hand_players:
                if player == nextup:
                    continue
                self.table.tell(f"Your cards: {player.hand.showhole(True)}", player)

        msg = f'{next_nick} is next to act. (${bet} to call)'
        self.table.say(msg, skip=[nextup])


    def act(self, new_hand=False):
        if not self.playing:
            return

        self.check_quitters()

        if not self.table.playing or self.table.n_in_hand < 2:
            self.end_hand()
            return

        # if self.table.nextup.intent is None:
        #     self.wait_for_action()
        #     return

        l(f"Evaluating actions for {self.table.nextup.nick}")
        advance = self.engine.run(new_hand)

        if not advance:
            return

        allin = True;
        while allin:
            table = self.table
            seats = table.seats
            seats.nextup = seats.after()
            player = table.nextup

            # End of round if next player is last bettor
            if table.seats.nextup == table.seats.last_bettor:
                l(f"Detected end of round.")

                # Unless it's preflop and we've limped to the big blind
                if table.round == PREFLOP and \
                       player == table.bb and not table.seats.big_blind_acted:

                    l(f"...Nevermind it's preflop big blind got limped to")

                    table.seats.last_bettor = seats.after(table.seats.bb)
                    seats.big_blind_acted = True
                else:
                    self.start_round()
                    return

            if not player.all_in:
                allin = False

        l(f"End of round not detected.")

        n_eligable = self.table.n_eligable
        n_quitters = self.table.n_quitters
        n_all_in = self.table.n_all_in

        # not enough players to continue
        l(f"Checking for enough players.")
        if not self.table.playing:
            self.flipout()
            return

        # heads up and both all in
        elif n_eligable == n_all_in or self.table.nextup.all_in:
            l(f"Heads up and both all in, starting new round.")
            self.start_round()
        else:
            self.wait_for_action()

    def settle_pot(self, pot, n_pots):
        winners = pot.award()
        n_winners = len(winners)
        share = pot.value / n_winners
        leftovers = pot.value % n_winners

        # Sort winners for odd chip distribution
        if leftovers and n_winners > 1:
            l('Distributing odd chips')
            winner_seat_order = winners[:]
            sorted = win_seat_sort(self.table.seats.button,
                                   self.table.players,
                                   winner_seat_order)

        for winner in winners:
            my_share = share
            # Distribute odd chip
            if leftovers and winner in sorted and (sorted.index(winner) < leftovers):
                l('%s gets extra chip' % winner.nick)
                my_share = share + 1
            winner.stack += my_share
            winner.total_winnings += my_share

            if n_pots == 1:
                l('%s wins $%d with %s %s' %\
                  (winner.nick, my_share,
                   Hand.TYPE_STR[winner.hand.type],
                   winner.hand.rankorderstr()))
                self.table.say('%s wins $%d with %s %s' %\
                               (winner.nick, my_share,
                             Hand.TYPE_STR[winner.hand.type],
                             winner.hand.rankorderstr()))
            else:
                # print 'return uncalled foo' for a pot with a
                # single player
                if len(pot.players) == 1:
                    l(f'Pot uncalled. ${pot.value} returned to {winner.nick}')
                    self.table.say('%s wins $%d' % (winner.nick, pot.value))
                else:
                    hand_type = Hand.TYPE_STR[winner.hand.type]
                    rank_order = winner.hand.rankorderstr()
                    msg = f'{winner.nick} wins ${my_share} with {hand_type} {rank_order}'
                    l(msg)
                    self.table.say(msg)

    def multi_showdown(self, in_hand_players):
        l("Multi Showdown!")
        # Compare hands and award pots
        l('Hand over, current board is: %s' % printboard(self.table))

        if self.table.n_in_hand - self.table.n_all_in > 1:
            self.table.say('Board:      %s' % printboard(self.table))
        self.table.say("Players hands:")

        longest_nick = self.table.longest_nick()

        for player in in_hand_players:
            for card in self.table.board:
                player.hand.addcard(card)

            self.table.say(player.hand_as_string(longest_nick))

        pots = self.table.pots.calculate(in_hand_players)
        n_pots = len(pots)
        for pot in pots:
            self.settle_pot(pot, n_pots)


    def solo_showdown(self, winner):
        l("Solo Showdown!")
        chips = self.table.pots.main
        winner.stack += chips
        winner.total_winnings += chips - winner.last_bet
        l('%s wins $%d' % (winner.nick, chips - winner.last_bet))
        self.table.say('%s wins $%d.' % (winner.nick, chips - winner.last_bet))


    def showdown(self):
        active = self.table.in_hand_players

        self.table.potsize[3] = self.table.pots.main
        self.table.nplyin[3] = len(active)

        if len(active) == 1:
            self.solo_showdown(active[0])
            showhole = False;
        else:
            self.multi_showdown(active)
            showhole = True;
        return showhole
