from __future__ import annotations
from typing import Callable, Optional
import numpy as np
from enum import Enum, IntEnum, auto
import random
import itertools
import math

from game_strategy import GameStrategy


__author__ = "Anton Höß"
__copyright__ = "Copyright 2021"


class _Dir(IntEnum):
    """Enumerates all possible moving directions."""

    LEFT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4
# end class


class _StrategyMove(Enum):
    """Enumerates the game strategy on how to choose the direction."""

    # XXX USER = auto()        # Let the user choose in each step
    RANDOM = auto()      # Choose random move direction
    ROTATE_CW = auto()   # Rotate clockwise
    ROTATE_CCW = auto()  # Rotate counterclockwise
    LDRD = auto()        # Left down, right down
    # AI_1 = auto()      # XXX Implement a more intelligent rule
# end class


class _StrategyTest(Enum):
    """Enumerates some dummy strategy values. This is only to show how it may work with multiple partial strategies,
    since this game only has one partial strategy."""

    T1 = auto()
    T2 = auto()
# end class


# Define types
_StrategySet = (_StrategyMove, )  # _StrategyTest)


class _PlotLoc(Enum):
    """Enumerates the plotting location within the algorithm."""

    INIT_BEFORE = auto()
    INIT_AFTER = auto()
    MOVE_TO_DIR_1_AFTER = auto()
    MERGE_NEIGHBOURS_AFTER = auto()
    MOVE_TO_DIR_2_AFTER = auto()
    ADD_NEW_NUMBER_AFTER = auto()
    GAME_OVER = auto()
# end class


class _Game2048ConsoleHelper:
    # For color codes see https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html#256-colors
    colors = dict()
    colors[1 << 1] = {"f": "8", "b": "253"}  # 2
    colors[1 << 2] = {"f": "8", "b": "187"}  # 4
    colors[1 << 3] = {"f": "15", "b": "215"}  # 8
    colors[1 << 4] = {"f": "15", "b": "172"}  # 16
    colors[1 << 5] = {"f": "15", "b": "9"}  # 32
    colors[1 << 6] = {"f": "15", "b": "160"}  # 64
    colors[1 << 7] = {"f": "15", "b": "229"}  # 128
    colors[1 << 8] = {"f": "15", "b": "228"}  # 256
    colors[1 << 9] = {"f": "15", "b": "227"}  # 512
    colors[1 << 10] = {"f": "15", "b": "226"}  # 1024
    colors[1 << 11] = {"f": "15", "b": "220"}  # 2048
    colors[1 << 12] = {"f": "15", "b": "0"}  # 4096
    colors[1 << 13] = {"f": "15", "b": "234"}  # 8192
    colors[1 << 14] = {"f": "15", "b": "236"}  # 16384
    colors[1 << 15] = {"f": "15", "b": "238"}  # 32768

    @classmethod
    def plot(cls, game: _Game2048, loc: _PlotLoc) -> None:
        if loc in (
                # _PlotLoc.INIT_BEFORE,
                _PlotLoc.INIT_AFTER,
                # _PlotLoc.MOVE_TO_DIR_1_AFTER,
                # _PlotLoc.MERGE_NEIGHBOURS_AFTER,
                # _PlotLoc.MOVE_TO_DIR_2_AFTER,
                _PlotLoc.ADD_NEW_NUMBER_AFTER,
                _PlotLoc.GAME_OVER,
        ):
            cls._plot(game)
        # end if

        if loc is _PlotLoc.GAME_OVER:
            print(f"Game over! You reached {game.points} points.")
        # end if
    # end def

    @classmethod
    def _plot(cls, game) -> None:
        w_m = np.ceil(np.log10(np.where(game.board == 0, 2, game.board)))
        w_max = np.max(w_m)

        for y in range(game.size):

            cells = list()
            for x in range(game.size):
                diff = w_max - w_m[y, x]
                if game.board[y, x] > 0:
                    fc_start = u"\u001b[38;5;" + cls.colors[game.board[y, x]]["f"] + "m"
                    bc_start = u"\u001b[48;5;" + cls.colors[game.board[y, x]]["b"] + "m"
                    c_end = "\u001b[0m"
                else:
                    fc_start = ""
                    bc_start = ""
                    c_end = ""
                cells.append(fc_start + bc_start + " " * math.ceil(diff / 2) + f"{game.board[y, x]}" +
                             " " * (math.floor(diff / 2)) + c_end)
            # end for
            print(" | ".join(cells))
        # end for

        print(f"Points: {game.points}")
    # end def

    @classmethod
    def get_move_dir(cls) -> _Dir:
        inp = -1

        while True:
            print("Enter a direction (" + ", ".join([f"{x.value}={x.name}" for x in list(_Dir)]) + "):")

            try:
                inp = int(input())

                if inp not in [x.value for x in list(_Dir)]:
                    print("No valid value entered! Try again!")
                    continue
                else:
                    break
                # end if
            except ValueError:
                print("No integer entered! Try again!")
                continue
            # end try
        # end while

        return _Dir(inp)
    # end def
# end class


class _Game2048:
    """Implements the game logic. Performs a single run of the game.
    For an algorithm see https://stackoverflow.com/questions/22342854/what-is-the-optimal-algorithm-for-the-game-2048
    """

    def __init__(self, strategy: _StrategySet, cb_get_move_dir: Callable[[], _Dir],
                 cb_plot: Optional[Callable[[_Game2048, _PlotLoc], None]], size: int = 4) -> None:
        """Initializes the game.

        Parameters
        ----------
        strategy : _StrategySet
            Set with a partial strategy of each type. Defines a full Strategy.
        cb_get_move_dir : Callable[[], _Dir]
            Callback for the user to choose the direction in the current step of the game.
        cb_plot : Callable[[_Game2048, _PlotLoc], None], optional
            Callback for the user to print the current tiles on the board.
        size : int, default 4
            Board size in x and y dimension.
        """

        self._strategy = strategy
        self._size = size
        self._board = np.zeros((size, size), dtype=int)
        self._cb_get_move_dir = cb_get_move_dir
        self._cb_plot = cb_plot
        self._points = 0
        self._cur_dir_idx = 0
    # end def

    @property
    def points(self):
        return self._points
    # end def

    @property
    def size(self):
        return self._size
    # end def

    @property
    def board(self):
        return self._board.copy()
    # end def

    def run(self) -> int:
        """Runs the game.

        Returns
        -------
        points : int
            The points achieved in this game.
        """

        # Step 1: Initialize the board with two initial numbers
        if self._cb_plot:
            self._cb_plot(self, _PlotLoc(_PlotLoc.INIT_BEFORE))

        self._phase_init()

        if self._cb_plot:
            self._cb_plot(self, _PlotLoc(_PlotLoc.INIT_AFTER))

        while True:
            # Step 2: Choose direction
            dir = self._phase_get_dir()

            # Step 3: Move all tiles into given direction
            action_performed = self._phase_move_to_dir(dir)

            if self._cb_plot:
                self._cb_plot(self, _PlotLoc(_PlotLoc.MOVE_TO_DIR_1_AFTER))

            # Step 4: Merge tiles of same value into given direction
            action_performed = self._phase_merge_neighbours(dir) or action_performed

            if self._cb_plot:
                self._cb_plot(self, _PlotLoc(_PlotLoc.MERGE_NEIGHBOURS_AFTER))

            # Step 5: Move again all (also merged) tiles into given direction
            self._phase_move_to_dir(dir)

            if self._cb_plot:
                self._cb_plot(self, _PlotLoc(_PlotLoc.MOVE_TO_DIR_2_AFTER))

            # Step 6: Add new number in any of the random tile if an effective move was performed
            if action_performed:
                self._add_new_number()

                if self._cb_plot:
                    self._cb_plot(self, _PlotLoc(_PlotLoc.ADD_NEW_NUMBER_AFTER))
            # end if

            # Step 7: Check if game has finished
            if action_performed and self._phase_check_game_over():
                if self._cb_plot:
                    self._cb_plot(self, _PlotLoc(_PlotLoc.GAME_OVER))
                break
            # end if
        # end while

        return self._points
    # end def

    def _add_new_number(self) -> None:
        """Adds a number (2 or 4) to an empty tile."""

        w = np.where(self._board == 0)
        cnt_free_cells = len(w[0])

        if cnt_free_cells > 0:
            idx = np.random.randint(cnt_free_cells)
            self._board[w[0][idx], w[1][idx]] = 2 if random.random() < .9 else 4
        # end if
    # end def

    def _phase_init(self) -> None:
        """Init phase. Adds initial numbers to the board."""

        self._add_new_number()
        self._add_new_number()
    # end def

    def _phase_get_dir(self) -> _Dir:
        """Get direction phase. Only in this function the strategy takes place.

        Returns
        -------
        dir : _Dir
            The move direction for this game cycle.
        """

        if self._strategy[0] is getattr(_StrategyMove, "USER", None):  # Callback that returns the (user) input
            return self._cb_get_move_dir()

        elif self._strategy[0] is getattr(_StrategyMove, "RANDOM", None):
            return random.choice(list(_Dir))

        elif self._strategy[0] is getattr(_StrategyMove, "ROTATE_CW", None):
            _cur_dir_idx = self._cur_dir_idx
            self._cur_dir_idx = (self._cur_dir_idx + 1) % len(_Dir)
            return list(_Dir)[_cur_dir_idx]

        elif self._strategy[0] is getattr(_StrategyMove, "ROTATE_CCW", None):
            _cur_dir_idx = self._cur_dir_idx
            self._cur_dir_idx = (self._cur_dir_idx - 1 + len(_Dir)) % len(_Dir)
            return list(_Dir)[_cur_dir_idx]

        elif self._strategy[0] is getattr(_StrategyMove, "LDRD", None):
            _cur_dir_idx = self._cur_dir_idx
            dirs = [_Dir.LEFT, _Dir.DOWN, _Dir.RIGHT, _Dir.DOWN, _Dir.UP]
            dir = _Dir(dirs[self._cur_dir_idx])
            self._cur_dir_idx = (self._cur_dir_idx + 1) % len(dirs)
            return dir

        #elif self._strategy is _StrategyMove.XXX:
        #    pass  # XXX
    # end def

    def _phase_move_to_dir(self, move_dir: _Dir) -> bool:
        """Moves all tiles into the given direction.

        Parameters
        ----------
        move_dir : _Dir
            The move direction.

        Returns
        -------
        action_performed : bool
            Indicates if an action has been performed.
        """

        action_performed = False

        # Move numbers to given direction
        if move_dir is _Dir.LEFT:  # For each row
            for r in range(self._size):  # For each column
                for c in range(1, self._size):
                    if self._board[r, c] != 0:
                        free_cells_cnt = len(np.where(self._board[r, 0:c] == 0)[0])
                        if free_cells_cnt > 0:
                            self._board[r, c - free_cells_cnt] = self._board[r, c]
                            self._board[r, c] = 0
                            action_performed = True
                        # end if
                    # end if
                # end for
            # end for

        elif move_dir is _Dir.UP:
            for c in range(self._size):  # For each column
                for r in range(1, self._size):  # For each row
                    if self._board[r, c] != 0:
                        free_cells_cnt = len(np.where(self._board[0:r, c] == 0)[0])
                        if free_cells_cnt > 0:
                            self._board[r - free_cells_cnt, c] = self._board[r, c]
                            self._board[r, c] = 0
                            action_performed = True
                        # end if
                    # end if
                # end for
            # end for

        elif move_dir is _Dir.RIGHT:
            for r in range(self._size):  # For each row
                for c in reversed(range(0, self._size - 1)):  # For each column
                    if self._board[r, c] != 0:
                        free_cells_cnt = len(np.where(self._board[r, c + 1:self._size] == 0)[0])
                        if free_cells_cnt > 0:
                            self._board[r, c + free_cells_cnt] = self._board[r, c]
                            self._board[r, c] = 0
                            action_performed = True
                        # end if
                    # end if
                # end for
            # end for

        elif move_dir is _Dir.DOWN:
            for c in range(self._size):  # For each column
                for r in reversed(range(0, self._size - 1)):  # For each row
                    if self._board[r, c] != 0:
                        free_cells_cnt = len(np.where(self._board[r + 1:self._size, c] == 0)[0])
                        if free_cells_cnt > 0:
                            self._board[r + free_cells_cnt, c] = self._board[r, c]
                            self._board[r, c] = 0
                            action_performed = True
                        # end if
                    # end if
                # end for
            # end for
        # end if

        return action_performed
    # end def

    def _phase_merge_neighbours(self, move_dir: _Dir) -> bool:
        """Merges neighbours of identical values into the given direction.

        Parameters
        ----------
        move_dir : _Dir
            The merge direction.

        Returns
        -------
        action_performed : bool
            Indicates if an action has been performed.
        """

        action_performed = False

        if move_dir in (_Dir.LEFT, _Dir.RIGHT):
            # For each row
            for r in range(self._size):
                # For each column (except the last one)
                for c in range(self._size - 1):
                    if self._board[r, c] != 0 and self._board[r, c] == self._board[r, c + 1]:
                        self._board[r, c] *= 2
                        self._points += self._board[r, c]
                        self._board[r, c + 1] = 0
                        action_performed = True
                    # end if
                # end for
            # end for

        elif move_dir in (_Dir.DOWN, _Dir.UP):
            # For each column
            for c in range(self._size):
                # For each row (except the last one)
                for r in range(self._size - 1):
                    if self._board[r, c] != 0 and self._board[r, c] == self._board[r + 1, c]:
                        self._board[r, c] *= 2
                        self._points += self._board[r, c]
                        self._board[r + 1, c] = 0
                        action_performed = True
                    # end if
                # end for
            # end for
        # end if

        return action_performed
    # end def

    def _phase_check_game_over(self) -> bool:
        """Checks if no more moves can be carried out and therefore the game is over.

        Returns
        -------
        game_over : bool
            Indicates if the game is over.
        """

        action_performable = False

        if len(np.where(self.board == 0)[0]) > 0:
            action_performable = True

        else:
            # Check _Dir.LEFT, _Dir.RIGHT
            for r in range(self._size):  # For each row
                if action_performable:
                    break

                for c in range(self._size - 1):  # For each column (except the last one)
                    if self._board[r, c] == self._board[r, c + 1]:
                        action_performable = True
                        break
                    # end if
                # end for
            # end for

            # Check _Dir.DOWN, _Dir.UP
            for c in range(self._size):  # For each column
                if action_performable:
                    break

                for r in range(self._size - 1):  # For each row (except the last one)
                    if self._board[r, c] == self._board[r + 1, c]:
                        action_performable = True
                        break
                    # end if
                # end for
            # end for
        # end if

        return not action_performable
    # end def
# end class


class GameStrategy2048(GameStrategy):
    """Analyzes the different game strategies and finds the best one."""

    def run_stats(self, n_rep_base: int = 1000, plot_auto: bool = False) -> None:
        """Runs the statistics by running many simulations and do some simple calculations.

        Parameters
        ----------
        n_rep_base : int, default 1000
            Base number of repetitions.
            Might be, that these number is internally modified (e.g. multiplied) on some places.
        plot_auto : bool, default False
            Indicates if the game shall be plotted in automatic (simulation) mode.
        """

        # Test all combinations of partial strategies
        #############################################
        all_points = list()
        all_partial_strategies_combinations = \
            list([(_StrategyMove(x[0]), ) for x in
                  itertools.product(*[[ps for ps in strategy] for strategy in (_StrategyMove, )])])

        self._print_header("Play the game each time with one of the following strategies:")
        for partial_strategy_combination in all_partial_strategies_combinations:
            print(tuple(str(partial_strategy) for partial_strategy in partial_strategy_combination))
        # end for

        for i, partial_strategy_combination in enumerate(all_partial_strategies_combinations):
            points = self._run_stats(
                n_rep=n_rep_base,
                strategy=partial_strategy_combination,
                plot_auto=plot_auto
            )
            all_points.append(points)

            # Print results
            print(f"\n# Test ({i + 1}/{len(all_partial_strategies_combinations)}) with the following strategy:")
            self._print_partial_strategy_combination(partial_strategy_combination)
            print(f"Points (avg): {points}")
        # end for

        # Print best strategy
        percentages = [points for points in all_points]
        max_index = percentages.index(max(percentages))
        self._print_header("==> The best strategy is:")
        self._print_partial_strategy_combination(all_partial_strategies_combinations[max_index])
    # end def

    def _run_stats(self, n_rep: int, strategy: _StrategySet, plot_auto: bool = False) -> float:
        """Runs the simulations and counts the wins.

        Parameters
        ----------
        n_rep : int
            Number of repetitions.
        strategy : _StrategySet
            A tuple containing the partial strategies.
        plot_auto : bool, default False
            Indicates if the game shall be plotted in automatic (simulation) mode.

        Returns
        -------
        points : float
            Average points achieved.
        """

        # Run simulations and count points
        points = 0

        if strategy[0] is getattr(_StrategyMove, "USER", None):
            n_rep = 1
        # end if

        for i in range(n_rep):
            points += self._run(strategy, plot_auto)
        # end for

        # Calculate average points
        points /= n_rep

        return points
    # end def

    @staticmethod
    def _run(strategy: _StrategySet, plot_auto: bool = False) -> float:
        """Creates a player's name. Only important for printing the statistics.

        Parameters
        ----------
        strategy : _StrategySet
            A tuple containing the partial strategy.
        plot_auto : bool, default False
            Indicates if the game shall be plottetd in automatic (simulation) mode.

        Returns
        -------
        points : float
            Average points achieved in each run.
        """

        console_helper = _Game2048ConsoleHelper()
        points = _Game2048(strategy=strategy,
                           cb_get_move_dir=console_helper.get_move_dir,
                           cb_plot=console_helper.plot if strategy[0] is getattr(_StrategyMove, "USER", None) or
                                                          plot_auto else None,
                           ).run()

        return points
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
# end class
