# who should store agent's position?
# if agent does, then world also has to because it needs to know which agents are at each location
# so let's not have agent store it
# then agent only knows things that don't depend on the world: sugar, metabolism, vision
# world can give agent a handle that helps world find out which agent is talking to it without keeping an extra lookup table

import itertools, random

def largest_values(iterable, *, key):
    maxval = max(iterable, key=key)
    return [x for x in iterable if key(x) == key(maxval)]

class Agent:
    next_id = 0

    def __init__(self, *, world, vision, metabolism, sugar, seed=None):
        self.id = self.next_id
        Agent.next_id += 1
        self.world = world
        self.vision = vision
        self.metabolism = metabolism
        self.sugar = sugar
        self.alive = True
        if seed is None:
            self.rng = random
        else:
            self.rng = random.Random(seed=seed)

    def update(self):
        if not self.alive:
            raise RuntimeError('agent is dead')
        self.eat()
        if not self.alive:
            return
        self.move()
        self.collect()

    def eat(self):
        self.sugar -= self.metabolism
        if self.sugar <= 0:
            self.alive = False
            self.world.remove(self)

    def move(self):
        own_position = self.world.position_of_agent[self]
        positions = [p for p in self.world.get_visible_points(own_position, self.vision) if self.world.agent_at_position[p] is None]
        positions.append(own_position)
        destinations = largest_values(positions, key=lambda p: (self.world.sugar[p], -self.world.grid.distance(own_position, p)))
        destination = self.rng.choice(list(destinations))
        self.world.move_agent(self, destination)

    def collect(self):
        # this is repeated twice, but it's safer in case we want something to happen between move() and collect()
        own_position = self.world.position_of_agent[self]
        self.sugar += self.world.sugar[own_position].amount
        self.world.sugar[own_position].amount = 0

    def __eq__(self, other):
        if not isinstance(other, Agent):
            raise TypeError
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)