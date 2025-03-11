import logging
import random

from reinforcement.agent import AgentQ
from reinforcement.joc import Laberint


def main():
    logging.basicConfig(
        format="%(levelname)-8s: %(asctime)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )  # Only show messages *equal to or above* this level

    game = Laberint()
    agent = AgentQ(game)
    h, w, _ = agent.train(
        discount=0.90,
        exploration_rate=0.10,
        learning_rate=0.6,
        episodes=1000,
        stop_at_convergence=True,
    )

    maze = game.maze

    for i in range(0,8):
        y = i
        for j in range(0,8):
            x = j
            if maze[i,j] == 1:
                #print(f"Posicion PROHIBIDA: ({x},{y}) \n")
                continue

            #print(f"Posicion: ({x},{y}) \n")
            game.reset((x, y))
            game.set_agent([agent])
            game.comencar()

if __name__ == "__main__":
    main()
