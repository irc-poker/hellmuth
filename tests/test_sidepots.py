import mock, pytest

mock.patch.dict('sys.modules', sopel=mock.MagicMock())

from .sopelmock import SopelMock, TriggerMock

from poker.sidepots import SidePots
from poker.dealer import Dealer
from poker.deck import Deck
from poker.table import Table
from poker.player import Player

@pytest.fixture
def table():
    return Table(SopelMock())

@pytest.fixture
def sidepots():
    return SidePots()

def test_setup(sidepots):
    sidepots.set()
    assert sidepots.has_side_pots

def test_reset(sidepots):
    sidepots.set()
    sidepots.reset()
    assert sidepots.has_side_pots == False

def test_main_pot_called(sidepots, mocker):
    mocker.patch('poker.sidepots.SidePots.calculate_side_pots')
    mocker.patch('poker.sidepots.SidePots.calculate_main_pot')
    sidepots.calculate([])
    sidepots.calculate_main_pot.assert_called()
    sidepots.calculate_side_pots.assert_not_called()

def test_side_pots_called(sidepots, mocker):
    mocker.patch('poker.sidepots.SidePots.calculate_side_pots')
    mocker.patch('poker.sidepots.SidePots.calculate_main_pot')
    sidepots.set()
    sidepots.calculate([])
    sidepots.calculate_main_pot.assert_not_called()
    sidepots.calculate_side_pots.assert_called()

def test_main_pot():
    bot = SopelMock()
    player1 = Player(bot, "player1")
    player1.quit = False
    player1.busted = False
    player1.folded = False

    players = [player1]
    sidepots = SidePots()
    sidepots.deposit(1000)
    pots = sidepots.calculate(players)

    assert pots
    assert len(pots) == 1
    assert pots[0].value == 1000
    assert player1 in pots[0].players

def test_side_pot(sidepots):
    bot = SopelMock()
    player1 = Player(bot, "player1")
    player1.stack = 1000
    player2 = Player(bot, "player2")
    player2.stack = 1000
    player3 = Player(bot, "player3")
    player3.stack = 1000

    players = [player1, player2, player3]

    dealer = Dealer(mock.MagicMock())
    dealer.deal_cards(Deck(), players, 0)

    player1.in_play = 25
    player2.in_play = 50
    player3.in_play = 100

    sidepots.set()
    pots = sidepots.calculate(players)
    assert pots
    assert len(pots) == 3
    assert pots[0].value == 75
    assert player1 in pots[0].players
    assert player2 in pots[0].players
    assert player3 in pots[0].players
    assert pots[1].value == 50
    assert player2 in pots[1].players
    assert player3 in pots[1].players
    assert pots[2].value == 50
    assert player3 in pots[2].players

def test_overbet(sidepots):
    bot = SopelMock()
    player1 = Player(bot, "player1")
    player2 = Player(bot, "player2")

    players = [player1, player2]

    dealer = Dealer(mock.MagicMock())
    dealer.deal_cards(Deck(), players, 0)

    player1.in_play = 25
    player2.in_play = 100

    sidepots.set()
    pots = sidepots.calculate(players)
    assert pots
    assert len(pots) == 2
    assert pots[0].value == 50
    assert player1 in pots[0].players
    assert player2 in pots[0].players
    assert pots[1].value == 75
    assert player2 in pots[1].players



