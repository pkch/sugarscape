import random
from collections import defaultdict
from itertools import repeat
import grids, world, distributions


def main():
    LENGTH = 50
    HEIGHT = 50
    SUGAR_CENTERS = ((15, 15), (35, 35))
    SUGAR_RANGES = (0, 5, 10, 15)
    SUGAR_GROWTH = float('inf')
    SUGAR_CIRCLE_P = 2
    N_AGENTS = 400
    SEED = 2
    METABOLISM = distributions.Uniform(1, 4)
    DISTANCE = distributions.Uniform(1, 6)
    INITIAL_SUGAR = 3
    VISION_P = 0

    random.seed(SEED)
    grid = grids.SquareGrid(LENGTH, HEIGHT)
    sugarscape = world.World(grid)

    for center in SUGAR_CENTERS:
        for radius in SUGAR_RANGES:
            for point in grid.get_circle(center, radius, p=SUGAR_CIRCLE_P):
                sugar = sugarscape.sugar[point]
                sugar.amount += 1
                sugar.capacity += 1
                sugar.growth = lambda a, c: SUGAR_GROWTH

    vision_gen = (grids.CircularVision(next(DISTANCE), p=VISION_P) for i in repeat(None))
    sugarscape.add_agents(N_AGENTS, metabolism_gen=METABOLISM, sugar_gen=repeat(INITIAL_SUGAR), vision_gen=vision_gen)
    sugarscape.interactive_run()

if __name__ == '__main__':
    main()