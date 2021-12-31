#!/usr/bin/env python


"""A simple collection of more or less primitive games and their (partial) simulations.
These simulations use different strategies (depending on the game) and allow to find the best strategy in less time."""


from hoppel_poppel import GameStrategyHoppelPoppel
from game_2048 import GameStrategy2048
import argparse
from enum import Enum


__author__ = "Anton Höß"
__copyright__ = "Copyright 2021"
__credits__ = list()
__license__ = "BSD"
__version__ = "0.1"
__maintainer__ = "Anton Höß"
__email__ = "anton.hoess42@gmail.com"
__status__ = "Development"


class Game(Enum):
    """Enumerate all games."""

    HOPPEL_POPPEL = "hoppel_poppel"
    GAME_2048 = "2048"
# end if


def main():
    """The main function running the program."""

    def check_positive(value):
        int_value = int(value)

        if int_value <= 0:
            raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")

        return int_value
    # end def

    # Read command line arguments
    parser = argparse.ArgumentParser(description="Simulates a game and prints some statistics which "
                                                 "helps to find the best game strategy.")
    parser.add_argument("-g", "--game", choices=[game.value for game in list(Game)], required=True,
                        help="Defines the game to simulate.")
    parser.add_argument("-n", "--n_rep", type=check_positive, required=False,
                        help="Defines the game to simulate.")
    parser.add_argument("-p", "--plot_auto", required=False, action="store_true",
                        help="Indicates if the game shall be visualized (if there's a visualization for the specific "
                             "game) in non-user-run (=simulation).")
    args = parser.parse_args()

    # Run selected game statistics
    if args.game == "hoppel_poppel":
        GameStrategyHoppelPoppel().run_stats(n_rep_base=100000 if not args.n_rep else args.n_rep)

    elif args.game == "2048":
        GameStrategy2048().run_stats(n_rep_base=100000 if not args.n_rep else args.n_rep, plot_auto=args.plot_auto)
    # end if
# end def


if __name__ == "__main__":
    main()
# end if
