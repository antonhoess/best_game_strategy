from abc import ABC, abstractmethod


__author__ = "Anton Höß"
__copyright__ = "Copyright 2021"


class GameStrategy(ABC):
    """The interface for game strategy classes."""

    @abstractmethod
    def _run(self, *args, **kwargs) -> int:
        """Performs a single run of the game.

        Parameters
        ----------
        *args
            Variable list of arguments.
        **kwargs
            Dictionary of keyword arguments.

        Returns
        -------
        winner_player_id : int
            The player ID (index) of the one that won.
        """

        pass
    # end def

    @abstractmethod
    def run_stats(self) -> None:
        """Runs the program multiple times for several testing scenarios and calculates the corresponding stats."""

        pass
    # end def
# end class
