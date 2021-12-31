from __future__ import annotations
from typing import List
from enum import Enum
import random
import itertools

from game_strategy import GameStrategy


__author__ = "Anton Höß"
__copyright__ = "Copyright 2021"


class _Color(Enum):
    """Enumerates the dice and animal colors."""

    RED = 1     # Rooster
    BLUE = 2    # Rabbit
    YELLOW = 3  # Duck
    GREEN = 4   # Cat
    WHITE = 5   # Place 2
    BLACK = 6   # Take one

    @classmethod
    def animals(cls) -> List[_Color]:
        return [_Color(cls.RED), _Color(cls.BLUE), _Color(cls.YELLOW), _Color(cls.GREEN)]
    # end def
# end class


class _StrategyDuplicates(Enum):
    """Enumerates the game strategy on how to choose which animals to place in the yellow area."""

    RANDOM = 1            # Choose random animals
    AVOID_DUPLICATES = 2  # Avoid duplicates whenever possible
    FORCE_DUPLICATES = 3  # Force duplicates whenever possible
# end class


class _StrategyTest(Enum):
    """Enumerates some dummy strategy values. This is only to show how it may work with multiple partial strategies,
    since this game only has one partial strategy."""

    T1 = 1
    T2 = 2
# end class


# Define types
_StrategySet = (_StrategyDuplicates, _StrategyTest)


class _Player:
    """Implements the game logic (from a player's perspective). Performs a single run of the game."""

    def __init__(self, strategy: _StrategySet) -> None:
        """Initializes the player.

        Parameters
        ----------
        strategy : _StrategySet
            Set with a partial strategy of each type. Defines a full Strategy.
        """

        self._animals = _Color.animals() * 2
        self._game_board = list()
        self._game_board_yellow_area = list()
        self._strategy = strategy
        self._strategy_duplicates = strategy[0]
        self._strategy_test = strategy[1]
    # end def

    def play(self) -> bool:
        """Performs one move.

        Returns
        ----------
        won : bool
            Indicates if the player has won.
        """

        # Step 1: Place max. two animals in the yellow are on the game board
        self._move_animal_to_game_board_yellow_area()

        # Step 2: Roll the die and perform action according to die color
        c = self._roll_die()

        if c is not _Color.BLACK:
            self._move_animal_to_game_board_game_area(c)
        else:
            self._take_animal_from_game_board_game_area()
        # end if

        # Step 3: Check if won and return this value
        return len(self._animals) == 0 and len(self._game_board_yellow_area) == 0
    # end def

    @staticmethod
    def _roll_die() -> _Color:
        """Rolls the die.

        Returns
        ----------
        color : _Color
            The rolled color.
        """

        return _Color(random.randint(1, 6))
    # end def

    def _move_animal_to_game_board_yellow_area(self) -> None:
        """Moves animals from outside the game board to the yellow area within the game board,
        applying the players strategy."""

        if self._strategy_duplicates is _StrategyDuplicates.RANDOM:
            for i in range(min(len(self._animals), 2 - len(self._game_board_yellow_area))):
                self._game_board_yellow_area.append(self._animals.pop(random.randrange(len(self._animals))))
                return
            # end for

        elif self._strategy_duplicates is _StrategyDuplicates.AVOID_DUPLICATES:
            # First, try to place duplicates from the animals list, but with the constraint
            # that there are no two same animals in the yellow area
            for slot in range(2 - len(self._game_board_yellow_area)):
                for c in _Color.animals():
                    if self._animals.count(c) == 2 and c not in self._game_board_yellow_area:
                        self._game_board_yellow_area.append(self._animals.pop(self._animals.index(c)))
                        return
                    # end if
                # end for
            # end for

            # If the yellow area is not full yet, try any animal, but again with the constraint
            # that there are no two same animals in the yellow area
            for slot in range(2 - len(self._game_board_yellow_area)):
                for c in _Color.animals():
                    if self._animals.count(c) == 1 and c not in self._game_board_yellow_area:
                        self._game_board_yellow_area.append(self._animals.pop(self._animals.index(c)))
                        return
                    # end if
                # end for
            # end for

            # If the yellow area is not full yet, try any animal without any constraint
            for slot in range(2 - len(self._game_board_yellow_area)):
                if len(self._animals) > 0:
                    self._game_board_yellow_area.append(self._animals.pop(random.randrange(len(self._animals))))
                    return
                # end if
            # end for
        # end if

        elif self._strategy_duplicates is _StrategyDuplicates.FORCE_DUPLICATES:
            if len(self._game_board_yellow_area) == 0 and len(self._animals) >= 2:
                # Place two animals of the same race in the yellow area whenever possible
                for c in _Color.animals():
                    if self._animals.count(c) == 2:
                        self._game_board_yellow_area.append(self._animals.pop(self._animals.index(c)))
                        self._game_board_yellow_area.append(self._animals.pop(self._animals.index(c)))
                        return
                    # end if
                # end for

            elif len(self._game_board_yellow_area) == 1 and len(self._animals) >= 1:
                # Place a second animal of the same race in the yellow area whenever possible
                for c in _Color.animals():
                    if self._animals.count(c) == 1 and c in self._game_board_yellow_area:
                        self._game_board_yellow_area.append(self._animals.pop(self._animals.index(c)))
                        return
                    # end if
                # end for
            # end if

            # Since there are no more duplicates outside the board, just fill the yellow area with random animals
            for slot in range(2 - len(self._game_board_yellow_area)):
                if len(self._animals) > 0:
                    self._game_board_yellow_area.append(self._animals.pop(random.randrange(len(self._animals))))
                    return
                # end if
            # end for
        # end if
    # end def

    def _move_animal_to_game_board_game_area(self, c: _Color) -> None:
        """Moves animals from the yellow area within the game board to the game area on the game board,
        applying the players strategy."""

        if c is _Color.WHITE:
            self._game_board.extend(self._game_board_yellow_area)
            self._game_board_yellow_area.clear()

        else:
            for a, animal in enumerate(self._game_board_yellow_area):
                if animal is c:
                    self._game_board.append(self._game_board_yellow_area.pop(a))
                    break
                # end if
            # end for
        # end if
    # end def

    def _take_animal_from_game_board_game_area(self) -> None:
        """Takes animals from the game area on the game board to outside the game board,
        applying the players strategy."""

        # In every case, the yellow area is always full or there are no more animals outside the game board.
        # So we need only to look on the animals on the game board.

        if len(self._game_board) > 1:
            if self._strategy_duplicates is _StrategyDuplicates.RANDOM:
                if len(self._game_board) > 0:
                    self._animals.append(self._game_board.pop(random.randrange(len(self._game_board))))
                    return
                # end if

            elif self._strategy_duplicates is _StrategyDuplicates.AVOID_DUPLICATES:
                # Take an animal where there are two of them on the game board to increase the chance since there are
                # probably more different colors to choose when rolling the die
                for c in _Color.animals():
                    if self._game_board.count(c) == 2:
                        self._animals.append(self._game_board.pop(self._game_board.index(c)))
                        return
                    # end if
                # end for

                # If there were no duplicates, choose a random one
                self._animals.append(self._game_board.pop(random.randrange(len(self._game_board))))
                return

            elif self._strategy_duplicates is _StrategyDuplicates.FORCE_DUPLICATES:
                # Take an animal where there are no two of them on the game board to decrease the chance since there are
                # probably less different colors to choose when rolling the die
                for c in _Color.animals():
                    if self._game_board.count(c) == 1:
                        self._animals.append(self._game_board.pop(self._game_board.index(c)))
                        return
                    # end if
                # end for

                # If there were only duplicates, choose a random one
                self._animals.append(self._game_board.pop(random.randrange(len(self._game_board))))
                return
            # end if
        # end if
    # end def
# end class


class GameStrategyHoppelPoppel(GameStrategy):
    """Analyzes the different game strategies and finds the best one."""

    def run_stats(self, n_rep_base: int = 1000) -> None:
        """Runs the statistics by running many simulations and do some simple calculations.

        Parameters
        ----------
        n_rep_base : int, default 1000
            Base number of repetitions.
            Might be, that these number is internally modified (e.g. multiplied) on some places.
        """

        # We mainly compare games of two players

        # Compare two players with a random strategy
        ############################################

        # Run simulations and count wins for every player
        wins = self._run_stats(n_rep=n_rep_base, player_strategies=[(_StrategyDuplicates.RANDOM, _StrategyTest.T1)] * 2)

        # Print results
        self._print_header("Two players with a random strategy:")
        print("Shows that the player that starts has a better chance to win.")
        self._print_stats_simple(wins)
        self._print_stats_crossover(wins)

        # Compare four players with a random strategy
        #############################################
        wins = self._run_stats(n_rep=n_rep_base, player_strategies=[(_StrategyDuplicates.RANDOM, _StrategyTest.T1)] * 4)

        # Print results
        self._print_header("Four players with a random strategy:")
        print("Shows how the chance to win chances by the players starting order.")
        self._print_stats_simple(wins)
        self._print_stats_crossover(wins)

        # Test all combinations of partial strategies
        #############################################
        all_wins = list()
        all_partial_strategies_combinations = \
            list([(_StrategyDuplicates(x[0]), _StrategyTest(x[1])) for x in
                  itertools.product(*[[ps for ps in strategy] for strategy in (_StrategyDuplicates, _StrategyTest)])])

        self._print_header("Two players - the first one with the random strategy, "
                           "the second one each time with one of the following strategies:")
        for partial_strategy_combination in all_partial_strategies_combinations:
            print(tuple(str(partial_strategy) for partial_strategy in partial_strategy_combination))
        # end for

        print("Only compare the wining rates of the second player. The partial strategy combination with the "
              "highest winning rate is simply the best strategy.")
        print("")

        for i, partial_strategy_combination in enumerate(all_partial_strategies_combinations):
            wins = self._run_stats(
                n_rep=n_rep_base,
                player_strategies=[(_StrategyDuplicates.RANDOM, _StrategyTest.T1), partial_strategy_combination])
            all_wins.append(wins)

            # Print results
            print(f"\n# Test ({i + 1}/{len(all_partial_strategies_combinations)}) with the following strategy:")
            self._print_partial_strategy_combination(partial_strategy_combination)
            self._print_stats_simple(wins)
        # end for

        # Print best strategy
        percentages = [wins[1] for wins in all_wins]
        max_index = percentages.index(max(percentages))
        self._print_header("==> The best strategy is:")
        self._print_partial_strategy_combination(all_partial_strategies_combinations[max_index])
    # end def

    def _run_stats(self, n_rep: int, player_strategies: List[_StrategySet]) -> dict:
        """Runs the simulations and counts the wins.

        Parameters
        ----------
        n_rep : int
            Number of repetitions.
        player_strategies : list of _StrategySet
            List with a tuple containing the partial strategies of each player.

        Returns
        -------
        wins : dict
            Dictionary with one entry for each player and their corresponding win count.
        """

        # Run simulations and count wins for every player
        wins = {i: 0 for i in range(len(player_strategies))}
        for i in range(n_rep):
            win = self._run(player_strategies)

            if win not in wins:
                wins[win] = 0
            # end if

            wins[win] += 1
        # end for

        return wins
    # end def

    @staticmethod
    def _get_player_name(index: int) -> str:
        """Creates a player's name. Only important for printing the statistics.

        Parameters
        ----------
        index : int
            Index of player.

        Returns
        -------
        player_name : str
            The created player's name.
        """

        return f"Player {index + 1}"
    # end def

    @staticmethod
    def _run(player_strategies: List[_StrategySet]) -> int:
        """Creates a player's name. Only important for printing the statistics.

        Parameters
        ----------
        player_strategies : list of _StrategySet
            List with a tuple containing the partial strategies of each player.

        Returns
        -------
        player_won : int
            Index of the player that has won this.
        """

        players = [_Player(strategy=strategy) for strategy in player_strategies]

        while True:
            for p, player in enumerate(players):
                if player.play():
                    return p
                # end if
            # end for
        # end while
    # end def

    @staticmethod
    def _print_partial_strategy_combination(partial_strategy_combination: _StrategySet) -> None:
        """Creates a player's name. Only important for printing the statistics.

        Parameters
        ----------
        partial_strategy_combination : _StrategySet
            A tuple containing the partial strategies defining a full strategy.
        """

        names = list()
        for partial_strategy in partial_strategy_combination:
            names.append((str(partial_strategy).split('.')[0], partial_strategy.name))
        # end for

        max_length = max([len(name[0]) for name in names])
        format_string = f"{{:<{max_length}}} = {{}}"

        for name in names:
            print(format_string.format(*name))
        # end for
    # end def

    @staticmethod
    def _print_header(header: str) -> None:
        """Prints a header in a certain format.

        Parameters
        ----------
        header : str
            The main header string.
        """

        print("\n")
        print(header)
        print("-" * len(header))
    # end def

    @classmethod
    def _print_stats_simple(cls, wins: dict) -> None:
        """Prints stats in simple form, i.e. one line per player.

        Parameters
        ----------
        wins : dict
            Dictionary with one entry for each player and their corresponding win count.
        """

        # Normalize number of wins (so that sum is 1)
        total = sum(value for value in wins.values())

        for player_index in wins.keys():
            wins[player_index] /= total
        # end for

        # Print title
        print("\n> Wins")

        # Print wins and normalized wins
        for k, v in sorted(wins.items()):
            print(cls._get_player_name(k) + f": {v * 100:6.2f}% -> {v * 100 * len(wins):6.2f}%")
        # end for
    # end def

    @classmethod
    def _print_stats_crossover(cls, wins: dict) -> None:
        """Prints stats in a more complex form, i.e. a cross over table with the winning rate quotients
        between each player with each other.

        Parameters
        ----------
        wins : dict
            Dictionary with one entry for each player and their corresponding win count.
        """

        # Create player names
        player_names = [cls._get_player_name(i) for i in range(len(wins))]
        name_max_len = max(8, *[len(name) for name in player_names])

        # Create table with winning quotient between player A and player B
        data = list()
        for player_a in range(len(wins)):
            data.append(list())
            for player_b in range(len(wins)):
                data[player_a].append(round(wins[player_a] / wins[player_b], 2))
            # end for
        # end for

        # Print title
        print("\n> Winning quotients of player A vs. player B (row vs column)")

        # Print quotients as table
        format_row = f"{{:>{name_max_len}}}" + f"{{:>{name_max_len + 2}}}" * len(player_names)

        # ... Header
        print(format_row.format(r"A \ B", *player_names))

        # ... Rows
        for team, row in zip(player_names, data):
            print(format_row.format(team, *[f"{value:.2f}" for value in row]))
        # end for
    # end def
# end class
