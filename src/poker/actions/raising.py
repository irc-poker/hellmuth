from .base_command import BaseCommand
from .callmax import CallMax

def l(msg):
    print(f"[RAISE] {msg}")

class Raise(BaseCommand):
    def __init__(self, amount):
        self.amount = int(amount)

    def insufficient_raise(self, table, player, seat, bet):
        # Raise too small
        pmin = min(self.maxraise, table.minraise)
        if bet == 0:
            self.fail(f'Insufficient bet.  Minimum bet is ${pmin}.')
        else:
            self.fail(f'Insufficient raise.  Minimum raise is ${pmin}.')

    def minor_shove(self, table, player, seat, bet):
        table.seats.last_bettor = table.players.index(player)
        table.minraise += player.stack - bet
        table.pots.deposit(player.jam())
        table.current_bet = player.action
        player.last_bet = player.action

        if table.n_all_in > 0:
            table.pots.set()

        msg = f'{player.nick} raises ${self.maxraise} and is all in.  Pot is ${table.pots.main}.'
        self.succeed(msg)

    def major_shove(self, table, player, seat):
        table.seats.last_bettor = table.players.index(player)

        table.pots.deposit(player.jam())
        player.last_bet = player.action

        if table.n_all_in > 0:
            table.pots.set()

        if table.current_bet == 0:
            msg = f'{player.nick} bets ${player.stack} and is all in.  Pot is now ${table.pots.main}.'
            self.succeed(msg)
        else:
            msg = f'{player.nick} raises ${player.stack - table.current_bet} and is all in.  Pot is now ${table.pots.main}.'
            self.succeed(msg)

        table.current_bet = player.action
        table.minraise = table.current_bet - table.minraise

    def normal_raise(self, table, player, seat, bet, chips):
        table.pots.deposit(player.pay(chips))
        table.seats.last_bettor = table.players.index(player)
        table.current_bet += self.amount
        table.minraise = self.amount
        player.last_bet = self.amount

        if table.n_all_in > 0:
            table.pots.set()

        if table.current_bet > 0:
            msg = f'{player.nick} raises ${self.amount}.  Pot is ${table.pots.main}.'
            self.succeed(msg)
        else:
            msg = f'{player.nick} bets ${self.amount}.  Pot is ${table.pots.main}.'
            self.succeed(msg)


    def minor_raise(self, table, player, seat, bet):
        self.maxraise = player.stack - bet

        if player.stack <= bet:
            # Not enough chips for the given raise
            self.fail('Insufficient chips to raise.  Please CALL or FOLD', player.nick)
        elif bet + table.minraise > player.stack and self.amount >= self.maxraise:
            l(f"{player.nick} raises via shove for ${bet}")
            self.minor_shove(table, player, seat, bet)
        else:
            l(f"{player.nick} raises with insufficient funds ${bet} > ${player.stack}")
            self.insufficient_raise(table, player, seat, bet)

    def major_raise(self, table, player, seat, bet):
        # Raise >= minimum raise
        if table.current_bet == 0:
            chips = self.amount
        else:
            chips = table.current_bet - player.action + self.amount

        if player.stack <= bet:
            # Not enough chips for the given raise
            l(f"{player.nick} raises with insufficient funds ${bet} > ${player.stack}")
            self.fail('Insufficient chips to raise.  Please .call or .fold')

        # All-in raise
        elif bet < player.stack <= chips:
            l(f"{player.nick} raises via shove to {self.amount}")
            self.major_shove(table, player, seat)

        # Normal raise
        else:
            l(f"{player.nick} raises for ${chips}")
            self.normal_raise(table, player, seat, bet, chips)

    def do_raise(self, table, player, seat, bet):
        # Raise too small?
        if self.amount < table.minraise:
            self.minor_raise(table, player, seat, bet)
        else:
            self.major_raise(table,player, seat, bet)

    def raise_bet(self, table, player, seat):
        bet = table.current_bet - player.action

        # 'raise $0' calls any bet
        if self.amount == 0:
            l(f"{player.nick} raises via call max")
            player.intent = CallMax()
        # Check to see if player was fully raised
        elif (table.current_bet == 0) or (table.current_bet - table.minraise >= player.last_bet):
            # OK to raise
            self.do_raise(table, player, seat, bet)

        else:
            l('%s raises when not fully raised' % player.nick)
            l(f'Current bet: ${table.current_bet}')
            l(f'Minraise: ${table.minraise}')
            l(f'{player.nick}\'s last bet: ${player.last_bet}')
            l(f'curbet - minraise >= last bet')
            self.fail('You were not fully raised and cannot raise.  Please .call or .fold')

    def run(self, table, player, seat):
        if table.nextup == table.bb:
            table.seats.big_blind_acted = True

        self.raise_bet(table, player, seat)

