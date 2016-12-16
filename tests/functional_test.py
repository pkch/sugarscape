import pytest
from itertools import repeat
import context
import grids, world

def create_simple_world():
    grid = grids.SquareGrid(5, 5)
    sugarscape = world.World(grid)

    for radius in (0, 1, 2):
        for point in grid.get_circle((1, 1), radius, p=2):
                sugar = sugarscape.sugar[point]
                sugar.amount += 1
                sugar.capacity += 1
                sugar.growth = lambda a, c: 2

    vision_gen = (grids.CircularVision(2, p=0) for i in repeat(None))
    sugarscape.add_agents(1, metabolism_gen=repeat(1), sugar_gen=repeat(3), vision_gen=vision_gen, position_gen=repeat((1, 4)))
    return sugarscape

def test_simple_world():
    sugarscape = create_simple_world()
    agent = sugarscape.agent_at_position[(1, 4)]
    assert sugarscape.position_of_agent[agent] == (1, 4)
    sugarscape.run(1)
    assert sugarscape.position_of_agent[agent] == (1, 1)


if __name__ == '__main__':
    sugarscape = create_simple_world()
    sugarscape.interactive_run()