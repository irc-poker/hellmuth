from sopel import module

from poker.table import Table
from poker.utils import printboard
from poker.decorators import with_table, with_player, unless_sitting, when_sitting


from poker.actions.quit import Quit
from poker.actions.call import Call
from poker.actions.fold import Fold
from poker.actions.check import Check
from poker.actions.bet import Bet
from poker.actions.raising import Raise
from poker.actions.jam import Jam
from poker.actions.pot import Pot


@module.commands("open")
@module.require_owner()
def open_table(bot, trigger):
    table = bot.memory.get("table", None)
    if table:
        bot.say("The poker table is already open.", trigger.nick)
        return

    bot.memory["table"] = Table(bot)
    bot.say("The poker table has been opened.", trigger.nick)

@module.commands("close")
@module.require_owner()
def close_table(bot, trigger):
    table = bot.memory.get("table", None)

    if table is None:
        bot.say("The poker table is not open.", trigger.nick)
    else:
        bot.memory["table"] = None
        bot.say("The poker table has been closed.", trigger.nick)

@module.commands("sit", "join")
@unless_sitting
def sit(bot, trigger, table, player):
    table.add_player(player)


@module.commands("buyin")
@with_table
@with_player
def buyin(bot, trigger, table, player):
    if not player in table.players:
        sit(bot, trigger)

    if player.bankroll == 0:
        bot.say("Sorry, you're broke. See .borrow to get more chips.", trigger.nick)
        return

    if not player.busted:
        bot.say("You can only buy in when busted. Your stack: ${player.stack}")
        return

    table.buyin(player)

@module.commands("start", "begin")
@when_sitting
def start(bot, trigger, table, player):

    if table.n_eligable < 2:
        bot.say("Need two or more players to begin.")
        return

    if table.dealer.playing:
        bot.say("Play has already started.")
        return

    table.dealer.start_session()


@module.commands("stand", "leave", "quit")
@when_sitting
def stand(bot, trigger, table, player):
    if table.dealer.playing:
        if player.stack > 0:
            table.tell(f"Your hand will be folded and {player.stack} chips returned to your bankroll.", player)
        player.quit = True
        intent = Quit()
        intent.run(table, player, None)
        if table.nextup == player:
            table.dealer.act()
    else:
        table.remove_player(player)

@module.commands("bankroll", "br")
@with_table
@with_player
def bankroll(bot, trigger, table, player):
    msg = f"You have ${player.bankroll} and {player.broke_chips} broke chip"
    if player.broke_chips == 1:
        msg += "."
    else:
        msg += "s."

    bot.say(msg, trigger.nick)

@module.commands("borrow")
@with_table
@with_player
def borrow(bot, trigger, table, player):
    if player.bankroll > 0:
        bot.say(f"You can only borrow when you're broke.", trigger.nick)
        bot.say(f"You have ${player.bankroll}.", trigger.nick)
        return

    player.bankroll += table.bankroll_amount
    player.broke_chips += 1

    msg = f"You now have ${player.bankroll} and {player.broke_chips} broke chip"
    if player.broke_chips == 1:
        msg += "."
    else:
        msg += "s."

    bot.say(msg, trigger.nick)

@module.commands("debug")
@with_table
@with_player
def debug(bot, trigger, table, player):
    seats = table.seats
    msg = f"""
Table -
playing: {table.playing}
board: {printboard(table)}
round: {table.round} hands: {table.hands}
pot: {table.pots.main}
current_bet: {table.current_bet} minraise: {table.minraise}

nplyin: {table.nplyin}
potsize: {table.potsize}

n_players: {table.n_players}
n_sitting: {table.n_sitting}
n_eligable: {table.n_eligable}
n_ineligable: {table.n_ineligable}
n_in_hand: {table.n_in_hand}
n_all_in: {table.n_all_in}
n_quitters: {table.n_quitters}

Seats-
nextup: {seats.nextup}
button: {seats.button}
bb: {seats.bb}
sb: {seats.sb}
last_bettor: {seats.last_bettor}
big_blind_acted: {seats.big_blind_acted} no_small_blind: {seats.no_small_blind}
button_should_advance: {seats.button_should_advance}

Players-
nextup: {table.nextup.nick}
button: {table.button.nick}
bb: {table.bb.nick}
sb: {table.sb.nick}
last_better: {table.last_bettor.nick}

"""
    print(msg)

    pots = table.pots.calculate(table.in_hand_players)
    print(f"Pots -")
    for idx, pot in enumerate(table.pots.pots):
        msg = f"""
Pot #{idx}: {pot.value}
          : {",".join([p.nick for p in pot.players])}
"""
        print(msg)

    for player in table.players:
        print(f"{player.nick} -")
        print(f"Command: {player.intent.__class__.__name__}")
        print(f"bankroll: {player.bankroll}")
        print(f"stack: {player.stack} old_stack {player.old_stack}")
        print(f"in_play: {player.in_play} action: {player.action}")
        print(f"won: {player.won} last_bet: {player.last_bet}")
        print(f"folded: {player.folded} busted: {player.busted}")
        print(f"quit: {player.quit} all_in: {player.all_in}")
        print(f"is_sitting: {player.is_sitting}")
        print(f"eligable: {player.eligable}")
        print(f"in_hand: {player.in_hand}")
        print("")


@module.commands("rel")
@with_table
@with_player
def after(bot, trigger, table, player):
    seats = table.seats
    players = table.players
    after = players[table.seats.after()]
    before = players[table.seats.before()]
    msg = f"""
Current player: {table.nextup.nick}
Player after: {after.nick}
Player before: {before.nick}
"""
    print(msg)

@module.commands("call")
@when_sitting
def call(bot, trigger, table, player):
    player.intent = Call("max")
    if player.nick == table.nextup.nick:
        table.dealer.act()

@module.commands("fold")
@when_sitting
def fold(bot, trigger, table, player):
    player.intent = Fold()
    if player == table.nextup:
        table.dealer.act()

@module.commands("check")
@when_sitting
def check(bot, trigger, table, player):
    player.intent = Check()
    if player == table.nextup:
        table.dealer.act()


@module.rule("^\.bet (.*)")
@when_sitting
def bet(bot, trigger, table, player):
    player.intent = Bet(trigger.group(1))
    if player == table.nextup:
        table.dealer.act()


@module.rule("^\.raise (.*)")
@when_sitting
def raise_bet(bot, trigger, table, player):
    player.intent = Raise(trigger.group(1))
    if player == table.nextup:
        table.dealer.act()

@module.commands("jam")
@when_sitting
def jam(bot, trigger, table, player):
    player.intent = Jam()
    if player == table.nextup:
        table.dealer.act()

@module.commands("pot")
@when_sitting
def pot(bot, trigger, table, player):
    player.intent = Pot()
    if player == table.nextup:
        table.dealer.act()

