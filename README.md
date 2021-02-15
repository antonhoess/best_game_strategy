# BestGameStrategy
A simple collection of more or less primitive games and their (partial) simulations. These simulations use different strategies (depending on the game) and allows to find the best strategy in less time.

## Install
### Create a conda environment
```bash
conda init bash # => Open new terminal
conda create --name best_game_strategy python=3.8
```

### Activate the conda environment and start the program
```bash
cd best_game_strategy/
conda activate best_game_strategy
./best_game_strategy.py --game=<GAME_NAME> --n_rep=100000  # See game names below at each game
```

## How to use the program
Choose a game and run the program as described above. Then just wait for the program to complete its simulations.
Then read and interpret the results printed to the command line. 


## List of games

### Hoppel Poppel (by HABA)
![Hoppel Poppel (HABA)](images/hoppel_poppel_haba.jpg "Hoppel Poppel (HABA)")

Manual: See [here](manuals/hoppel_poppel_haba.pdf).

Game name: `hoppel_poppel`



