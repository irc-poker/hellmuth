from .hand import Hand

class Pot:
    def __init__(self):
        self.value = 0
        self.players = []

    def award(self):
        hands = []
        for p in self.players:
            p.hand.evaluate()
            hands.append(p.hand)
            p.hand.seat = self.players.index(p)

        hands.sort()
        hands.reverse()

        # Determine the number of winners
        hwinners = []
        hwinners.append(hands[0])
        for x in range(len(hands) - 1):
            h1 = hands[x]
            h2 = hands[x + 1]
            if h1 == h2:
                hwinners.append(h2)
            else:
                break

        winners = []
        for hw in hwinners:
            winners.append(self.players[hw.seat])

        return winners

    def inpot(self, p):
        result = False

        for player in self.players:
            if p.nick == player.nick:
                result = True

        return result
