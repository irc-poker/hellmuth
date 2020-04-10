import functools
from sopel import module

from poker.player import Player


def while_true(*properties):
    def decorator(func):
        @functools.wraps(func)
        def inner(bot, trigger):
            for prop in properties:
                if not bot.get_nick_value(trigger.nick, prop):
                    return

            func(bot, trigger)

        return inner

def unless_true(*properties):
    def decorator(func):
        @functools.wraps(func)
        def inner(bot, trigger):
            for prop in properties:
                if bot.get_nick_value(trigger.nick, prop):
                    return

            func(bot, trigger)

        return inner

def with_table(func):
    @functools.wraps(func)
    def inner(bot, trigger, *args):
        table = bot.memory.get("table")
        if not table:
            bot.say("The poker table is not open.", trigger.nick)
            return
        args = args + (table,)
        func(bot, trigger, *args)
    return inner

def with_player(func):
    @functools.wraps(func)
    def inner(bot, trigger, *args):
        player = Player(bot, trigger.nick)

        table = bot.memory.get("table")
        if table:
            existing_player = table.named_player(player.nick)
            if existing_player:
                player = existing_player

        args = args + (player,)
        func(bot, trigger, *args)
    return inner

def unless_sitting(func):
    @with_table
    @with_player
    @functools.wraps(func)
    def inner(bot, trigger, table, player):
        if player in table.players:
            bot.say("You can't do that while sitting at the table.")
            return
        func(bot, trigger, table, player)
    return inner

def when_sitting(func):
    @with_table
    @with_player
    @functools.wraps(func)
    def inner(bot, trigger, table, player):
        if not player in table.players:
            bot.say("You need to be sitting at the table to do that.")
            return
        func(bot, trigger, table, player)
    return inner


def can_act(func):
    @with_table
    @with_player
    @functools.wraps(func)
    def inner(bot, trigger, table, player):
        if player.busted:
            bot.say("You can't do that because you're busted.")
            return

        if player.all_in:
            bot.say("You can't do that because you're all in.")
            return

        func(bot, trigger, table, player)
    return inner

