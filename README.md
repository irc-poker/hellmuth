# Hellmuth

Hellmuth is an IRC bot that hosts No-limit Texas Holdem.

## Getting started

Download or clone this source. Copy the configuration template to a new name:

    $ git clone ....
    $ cd hellmuth/cfg
    $ cp -r template freenode

Then edit the configuration inside `hellmuth/cfg/freenode/default.cfg` with your own settings.

### Running with Docker

The easiest way to run Hellmuth is with Docker via the Makefile. Just pass the name of your configuration above. In this case, `freenode`:

    $ make freenode

That will build the Docker image and boot the container. Your bot should come online and say hello.

### Running without Docker

    TODO

## Operating the Bot

The bot has three primary commands:

-  `.open` Make the poker table available
-  `.close` Make the poker table unavailable
-  `.start` Start play, once at least 2 players have bought in


## Joining the Game

The following commands will help players get joined up:

-  `.bankroll` Check how many chips you have
-  `.borrow` Borrow more chips when you're broke
-  `.sit` Sit at the table, but don't buy in
-  `.buyin` (implies .sit) Buy in and play poker
-  `.stand` Leave the table, depositing your stack

## Playing the Game

Once play begins, the follow commands are available:

- `.fold` Fold your hand
- `.check` Check to the next player
- `.call` Call the current bet
- `.bet X` Bet $X
- `.raise X` Raise bet to $X

Play will continue as long as there are two or more players with non-zero stacks.