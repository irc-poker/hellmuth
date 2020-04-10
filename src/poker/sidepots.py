from .pot import Pot

def l(msg):
    print(f"[SIDEPOTS] {msg}")

class SidePots:

    def __init__(self):
        self.main = 0
        self.has_side_pots = False

    def set(self):
        self.has_side_pots = True

    def reset(self):
        self.main = 0
        self.has_side_pots = False

    def deposit(self, amount):
        self.main += amount

    def calculate_main_pot(self, players):
        l("Calculating MAIN POT.")
        pot = Pot()
        pot.value = self.main
        pot.players = players
        return [pot]

    def calculate_side_pots(self, players):
        l("Calculating SIDEPOTS.")
        pots = []
        players = sorted(players, key=lambda o: o.in_play)

        for player in players:
            l(f"{player.nick}: ${player.in_play}")

        while len(players):
            player = players.pop(0)

            if not player.in_play > 0:
                break

            # create new pot
            pot = Pot()

            # add current player to pot
            pot.players.append(player)
            # add current amount to pot
            pot.value += player.in_play

            # subtract trigger amount from other player's action
            for o in players:
                pot.players.append(o)
                pot.value += player.in_play
                o.in_play -= player.in_play

            # clear original player's action
            player.in_play = 0

            # save new pot
            pots.append(pot)

        return pots

    def calculate(self, players):
        if self.has_side_pots:
            pots = self.calculate_side_pots(players)
        else:
            pots = self.calculate_main_pot(players)

        for pot in pots:
            nicklist = [p.nick for p in pot.players]
            nicks = ",".join(nicklist)
            l(f'Added ${pot.value} pot for: {nicks}')

        return pots
