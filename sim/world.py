import random
from itertools import count
import resources, agents

class World:
    def __init__(self, grid, seed=None):
        self.grid = grid

        # these should be factored out to an indexed lookup table with 2 columns
        self.agent_at_position = {p: None for p in self.grid.get_all_points()} # {position: agent or None}
        self.position_of_agent = {} # {agent: position}; this is also the way to get all agents

        self.sugar = {p: resources.Sugar() for p in self.grid.get_all_points()}

        self.t = 0

        if seed is None:
            self.rng = random
        else:
            self.rng = random.Random(seed=seed)

    # always uniformly distributed without colliding
    def add_agents(self, n, *, vision_gen, metabolism_gen, sugar_gen, position_gen=None):
        if position_gen is None:
            unoccupied_positions = [p for p in self.agent_at_position if not self.agent_at_position[p]]
            position_gen = iter(self.rng.sample(unoccupied_positions, n))
        for i in range(n):
            position = next(position_gen)
            vision = next(vision_gen)
            metabolism = next(metabolism_gen)
            sugar = next(sugar_gen)
            agent = agents.Agent(world=self, vision=vision, metabolism=metabolism, sugar=sugar)
            self.agent_at_position[position] = agent
            self.position_of_agent[agent] = position

    def remove(self, agent):
        p = self.position_of_agent[agent]
        del self.position_of_agent[agent]
        self.agent_at_position[p] = None

    def get_visible_points(self, point, vision):
        return vision.get_visible_points(self.grid, point)

    def get_n_agents(self):
        return len(self.position_of_agent)

    def move_agent(self, agent, destination):
        if self.position_of_agent[agent] == destination:
            return
        if self.agent_at_position[destination] is not None:
            raise RuntimeError('Cannot move agent to an occupied spot')
        p = self.position_of_agent[agent]
        self.position_of_agent[agent] = destination
        self.agent_at_position[p] = None
        self.agent_at_position[destination] = agent

    def run(self, steps=1):
        for step in range(steps):
            self.step()

    def step(self):
        agents = list(self.position_of_agent)
        self.rng.shuffle(agents)
        for agent in agents:
            agent.update()
        for position, sugar in self.sugar.items():
            sugar.update()

    @classmethod
    def display_matrix(cls, matrix):
        hl = ' ' + '-' * (len(matrix[0]) * 2 - 1) + '\n'
        return hl + '\n'.join('|' + ' '.join(row) + '|' for row in matrix) + '\n' + hl

    def display(self, *, show_sugar=False):
        matrix = [[self.display_cell(y=self.grid.height-row-1, x=col, show_sugar=show_sugar) for col in range(self.grid.length)] for row in range(self.grid.height)]
        return self.display_matrix(matrix)

    def display_cell(self, *, x, y, show_sugar=False):
        if self.agent_at_position[x, y]:
            return '*'
        elif show_sugar:
            return str(self.sugar[x, y].amount)
        else:
            return ' '

    def interactive_run(self, show_sugar=False):
        print(self.display(show_sugar=show_sugar))
        for i in count():
            s = input()
            if s != '':
                break
            print('step', i)
            self.step()
            print(self.display(show_sugar=show_sugar))
