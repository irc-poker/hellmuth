
def l(msg):
    print(f"[TRACKER] {msg}")

class SeatTracker:
    def __init__(self, table):
        self.table = table
        self.new_session()

    def new_session(self):
        self.button = 0

        if len(self.table.players) == 2:
            self.sb = 0
            self.bb = 1
        else:
            self.sb = 1
            self.bb = 2

        self.nextup = 0
        self.last_bettor = 0
        self.button_should_advance = False
        self.big_blind_acted = False
        self.no_small_blind = False

    def after(self, seat=-1):
        '''Return the seat number of the player who will be next to
        act after the current active player.

        An optional argument allows you to get the player who will be
        next to act after an arbitrary seat, specified by an integer
        seat number.'''
        if seat >= 0:
            oldas = seat
        else:
            oldas = self.nextup
        n_players = len(self.table.players)
        if oldas >= n_players:
            oldas = n_players - 1
        for offset in range(1, n_players):
            newas = (oldas + offset) % n_players
            if(not self.table.players[newas].folded and
               not self.table.players[newas].busted):
                return newas
        return oldas

    #FIXME:  This probably needs modified for Player.quit
    def before(self, seat=-1):
        '''Return the seat number of the player to the right of
        the specified player.
        '''
        if seat >= 0:
            oldas = seat
        else:
            oldas = self.nextup

        if oldas == 0:
            newas = self.table.n_players - 1
        else:
            newas = oldas - 1

        while newas != oldas:
            if(not self.table.players[newas].folded and
               not self.table.players[newas].busted):
                return newas
            if newas == 0:
                newas = self.table.n_players - 1
            else:
                newas -= 1
        return oldas

    def update_sb(self):
        if self.no_small_blind:
            return

        # the small blind is last hand's big blind
        self.sb = self.bb

    def update_bb(self):
        # big blind always advances as normal
        self.bb = self.after(self.bb)

    def update_button(self):
        # advance button as normal
        if self.button_should_advance:
            # so move button forwards
            self.button = self.after(self.button)
        # button delayed but button holder eliminated
        elif self.table.button.busted:
            # so move button backwards
            self.button = self.before(self.button)

    def advance_party(self):
        # by default the button should advance
        self.button_should_advance = True

        # by default there is a small blind
        self.no_small_blind = False

        # if small blind busted last hand
        if self.table.sb.busted:
            # delay the button this hand
            self.button_should_advance = False

        # if the big blind busted last hand
        if self.table.bb.busted:
            # then there is no small blind this hand
            self.no_small_blind = True
            # and the button does not advance
            self.button_should_advance = False

        self.update_sb()

        l(f"Post-sb:")
        l(f"Button: {self.table.button.nick} {self.button}")
        l(f"Small Blind: {self.table.sb.nick} {self.sb}")
        l(f"Big Blind: {self.table.bb.nick} {self.bb}")
        l(f"-----")

        self.update_bb()

        l(f"Post-bb:")
        l(f"Button: {self.table.button.nick} {self.button}")
        l(f"Small Blind: {self.table.sb.nick} {self.sb}")
        l(f"Big Blind: {self.table.bb.nick} {self.bb}")
        l(f"-----")

        self.update_button()

    def advance_headsup(self):
        # Heads-up
        self.bb = self.after(self.bb)
        self.sb = self.after(self.bb)
        self.button = self.sb

    def advance_button(self):
        self.big_blind_acted = False

        l(f"Initial:")
        l(f"Button: {self.table.button.nick} {self.button}")
        l(f"Small Blind: {self.table.sb.nick} {self.sb}")
        l(f"Big Blind: {self.table.bb.nick} {self.bb}")
        l(f"-----")

        if self.table.n_in_hand >= 3:
            if self.button == self.sb:
                l(f"Button == Small Blind: {self.button} {self.sb}")
                l(f"Advancing Small Blind: {self.sb} => {self.after(self.bb)}")
                l(f"-----")
                self.sb = self.after(self.button)
                self.bb = self.after(self.sb)
                l(f"Pre-update:")
                l(f"Button: {self.table.button.nick} {self.button}")
                l(f"Small Blind: {self.table.sb.nick} {self.sb}")
                l(f"Big Blind: {self.table.bb.nick} {self.bb}")
                l(f"-----")
            self.advance_party()
        else:
            self.advance_headsup()

        self.nextup = self.after(self.bb)

        l(f"Final:")
        l(f"Action: {self.table.nextup.nick}")
        l(f"Button: {self.table.button.nick} {self.button}")
        l(f"Small Blind: {self.table.sb.nick} {self.sb}")
        l(f"Big Blind: {self.table.bb.nick} {self.bb}")
