from inflect import engine

inflector = engine()

from .constants import *

def cmp(a, b):
    if hasattr(a, "__cmp__"):
        return a.__cmp__(b)

    else:
        if a < b:
            return -1
        if a == b:
            return 0
        return 1

def printboard(table):
    buf = ''
    if table.round == PREFLOP:
         buf += ''
    if table.round == FLOP:
        for n in range(3):
            buf += table.board[n].face(True) + ' '
    if table.round == TURN:
        for n in range(4):
            buf += table.board[n].face(True) + ' '
    if table.round == RIVER:
        for n in range(5):
            buf += table.board[n].face(True) + ' '
    return buf

def plural(word, count):
    if count == 1:
        return word
    return inflector.plural(word)

do_debug = True

def debug(func):
    def inner(*args):
        if do_debug:
            print(f"{func.__name__} ({args})")
        func(*args)
    return inner


def win_seat_sort(self, button, players, order):
    '''Sort the winners of a multiway pot clockwise from the dealer.'''
    sorted = []
    n_players = len(players)

    for i in range(n_layers):
        seat = (button + i + 1) % n_players
        for p in order:
            if p.nick == players[seat].nick:
                sorted.append(p)
                order.remove(p)
                break
    return sorted
