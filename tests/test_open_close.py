import mock, pytest

mock.patch.dict('sys.modules', sopel=mock.MagicMock())

from .sopelmock import SopelMock, TriggerMock

from poker import open_table, close_table
from poker.table import Table

@pytest.fixture
def bot():
    return SopelMock()

@pytest.fixture
def trigger():
    return TriggerMock()

def test_open(bot, trigger):
    assert bot.memory.get("table") is None
    open_table(bot, trigger)
    table = bot.memory.get("table")
    assert table is not None
    assert isinstance(table, Table)

def test_already_open(bot, trigger):
    open_table(bot, trigger)
    table = bot.memory.get("table")
    open_table(bot, trigger)
    table2 = bot.memory.get("table")
    assert id(table) == id(table2)

def test_close(bot, trigger):
    open_table(bot, trigger)
    close_table(bot, trigger)
    table = bot.memory.get("table")
    assert table is None

def test_already_closed(bot, trigger):
    close_table(bot, trigger)
    bot.say.assert_called_with("The poker table is not open.", trigger.nick)


