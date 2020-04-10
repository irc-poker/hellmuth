import mock, pytest

mock.patch.dict('sys.modules', sopel=mock.MagicMock())

from .sopelmock import SopelMock, TriggerMock

from poker.sidepots import SidePots
from poker.dealer import Dealer
from poker.deck import Deck
from poker.table import Table
from poker.player import Player
from poker.actions.fold import Fold
from poker.actions.jam import Jam
from poker.actions.raising import Raise
from poker.actions.call import Call
from poker.actions.bet import Bet


@pytest.fixture
def bot():
    return SopelMock()

@pytest.fixture
def table():
    table = Table(SopelMock())
    table.shuffle_players = False
    table.say = lambda msg, *args, **kwargs: print(f"====> {msg}")
    return table

def test_game(table):
    player1 = Player(table.bot, "player1")
    player1.bankroll = table.max_buyin
    player2 = Player(table.bot, "player2")
    player2.bankroll = table.max_buyin

    table.add_player(player1)
    table.buyin(player1)

    table.add_player(player2)
    table.buyin(player2)

    table.dealer.start_session(True)

    player1.intent = Fold()
    table.dealer.act()

    assert player1.total_action == 15
    assert player2.total_action == 30
    assert player1.total_winnings == 0
    assert player2.total_winnings == 45



def test_jam(table):
    player1 = Player(table.bot, "player1")
    player1.bankroll = table.max_buyin
    player2 = Player(table.bot, "player2")
    player2.bankroll = table.max_buyin

    table.add_player(player1)
    table.buyin(player1)

    table.add_player(player2)
    table.buyin(player2)

    table.deck.reseed(True)
    table.dealer.start_session(True)

    player1.intent = Jam()
    player2.intent = Jam()
    table.dealer.act()

    assert player1.total_action == 1000
    assert player2.total_action == 1000
    assert player1.total_winnings == 2000
    assert player2.total_winnings == 0


def test_raise(table):
    player1 = Player(table.bot, "player1")
    player1.bankroll = table.max_buyin
    player2 = Player(table.bot, "player2")
    player2.bankroll = table.max_buyin

    table.add_player(player1)
    table.buyin(player1)

    table.add_player(player2)
    table.buyin(player2)

    table.deck.reseed(True)
    table.dealer.start_session(True)

    player1.intent = Raise(40)
    player2.intent = Call()
    table.dealer.act()

    player1.intent = Raise(100)
    player2.intent = Raise(100)
    table.dealer.act()

    player1.intent = Call()
    player2.intent = Fold()
    table.dealer.act()

    assert player1.total_action == 270
    assert player2.total_action == 170
    assert player1.total_winnings == 340
    assert player2.total_winnings == 0

def test_multi(table):
    player1 = Player(table.bot, "player1")
    player1.bankroll = table.max_buyin
    player2 = Player(table.bot, "player2")
    player2.bankroll = table.max_buyin
    player3 = Player(table.bot, "player3")
    player3.bankroll = table.max_buyin

    table.add_player(player1)
    table.buyin(player1)

    table.add_player(player2)
    table.buyin(player2)

    table.add_player(player3)
    table.buyin(player3)

    table.deck.reseed(True)
    table.seats.advance_button()
    table.dealer.start_session(True)

    player1.intent = Raise(40)
    player2.intent = Call()
    player3.intent = Call()
    table.dealer.act()

    player2.intent = Raise(100)
    player3.intent = Raise(100)
    player1.intent = Raise(100)
    table.dealer.act()

    player2.intent = Fold()
    player3.intent = Call()
    table.dealer.act()

    player3.intent = Jam()
    player1.intent = Call()
    table.dealer.act()

    assert player1.total_action == 1000
    assert player2.total_action == 170
    assert player3.total_action == 1000
    assert player1.total_winnings == 0
    assert player2.total_winnings == 0
    assert player3.total_winnings == 2000


# def test_bet(table):
#     table.tell = mock.MagicMock()
#     player1 = Player(table.bot, "player1")
#     player1.bankroll = table.max_buyin
#     player2 = Player(table.bot, "player2")
#     player2.bankroll = table.max_buyin

#     table.add_player(player1)
#     table.buyin(player1)

#     table.add_player(player2)
#     table.buyin(player2)

#     table.deck.reseed(True)
#     table.dealer.start_session(True)

#     player1.intent = Call()
#     player2.intent = Call()
#     table.dealer.act()

#     player2.intent = Bet(50)
#     player1.intent = Raise(20)
#     table.dealer.act()

#     player2.intent = Raise(1)
#     table.dealer.act()

#     # assert player1.total_action == 1000
#     # assert player2.total_action == 170
#     # assert player3.total_action == 1000
#     # assert player1.total_winnings == 0
#     # assert player2.total_winnings == 0
#     # assert player3.total_winnings == 2000
#     assert False
