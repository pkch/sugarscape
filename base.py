# grid: geometry (square) + topology (torus) + directions (need for some types of vision)
#   if we didn't need direction, we could model this as a graph - but with so much regularity that it may simpler to model as a grid anyway
# sugar distribution: dict: point -> (level, capacity) (or several dictionaries)
# sugar regeneration: f: level(t), capacity, point -> level(t+1)
# agent state:
#   variable: position, sugar
#   fixed: metabolism, vision
# agent behavior: find nearest unoccupied position of max sugar within vision, go there and collect sugar; ties broken randomly
#   vision: NESW only, up to vision
#   movement order: random
# ? vision in a circle?
# ? movement speed != vision distance (+ change target if not finished move)
# ? move simultaneously (without coordinating) => might end up in the same location, have to resolve that

# design problems
# draft 1:
# simulation contains grid, agents, sugar; grid and sugar are custom collections, agents is just a list of agents -- inconsistent, not good
# grid contains points
# points know geometry/topology, but not completely (points don't know the grid they are part of so for vision need to get the entire grid) -- inconsistent, not good
# agents know their behavior; contain points grid, sugar, other agents -- too much, not good
# sugar knows its behavior; also knows about grid -- feels like they should be tied together somehow, not good
# if we make agent know less then simulation has to know about agent behavior, also not good 

# draft 2:
# simulation contains grid, agents, sugar

import pytest, functools

class Point:
    def __init__(self, *coords):
        self.coords = coords
            
    # need eq and hash for use as keys in sets/dict (and comparisons for ==)
    def __eq__(self, other):
        return type(self) == type(other) and self.coords == other.coords
    
    def __hash__(self):
        return hash(self.coords)
    
    def __repr__(self):
        return self.__class__.__name__ + ': ' + ', '.join(map(str, self.coords))
    
    def validate_dimensions(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('lhs and rhs have different dimensions')
        
    def __add__(self, other):
        self.validate_dimensions(other)
        if not isinstance(other, Direction):
            raise NotImplemented
        # Point + Direction -> Point
        return Point(*[s + o for s, o in zip(self.coords, other.coords)])
    
class WrapAroundPoint(Point):
    # we could have modified __eq__ and __hash__ (and __repr__) instead of __add__, but then dict lookup will be very expensive
    def __init__(self, *coords, limits):
        if len(coords) != len(limits):
            raise ValueError('coords and limits dimensions do not match')
        super().__init__(*coords)
        self.limits = limits
        
    def __add__(self, other):
        self.validate_dimensions(other)
        if not isinstance(other, Direction):
            raise NotImplemented
        return WrapAroundPoint(*[(s + o) % limit for s, o, limit in zip(self.coords, other.coords, self.limits)], limits=self.limits)
    
class Direction(Point):
    def __add__(self, other):
        self.validate_dimensions(other)
        if not isinstance(other, Direction):
            raise NotImplemented
        # Direction + Direction -> Direction
        return Direction(*[s + o for s, o in zip(self.coords, other.coords)])

    def __mul__(self, num):
        return Direction(*[s * num for s in self.coords])
    
    def __rmul__(self, num):
        return self * num
        
class SquareGrid:
    N = Direction(0, 1)
    E = Direction(1, 0)
    S = Direction(0, -1)
    W = Direction(-1, 0)
    PRINCIPAL_DIRECTIONS = (N, E, S, W)
    def __init__(self, length, height, wraparound=True):
        self.limits = (length, height)
        self.wraparound = wraparound
        # not sure if get_point should be part of public API; if not, we'll need to add methods to produce a circle around a given point, etc. - how many methods? do we have to add more all the time? 
        if wraparound:
            self.get_point = functools.partial(WrapAroundPoint, limits=self.limits)
        else:
            self.get_point = Point
        #self._map = {self.get_point(x, y) for x in range(length) for y in range(height)}

    def get_circle(self, position, radius, p):
        # must avoid repeating the same point twice (not just performance, but semantics)
        circle = set()
        
        if p == 0:
            circle.add(position)
            for direction in self.PRINCIPAL_DIRECTIONS:
                for d in range(1, radius+1):
                    circle.add(position + d * direction)
        else:
            for delta_x in range(-radius, radius+1):
                for delta_y in range(-radius, radius+1):
                    if p == float('inf') or delta_x ** p + delta_y ** p <= radius ** p:
                        circle.add(position + delta_x * self.E + delta_y * self.N)        
        return circle
    
    def get_all_points(self):
        length, height = self.limits
        return (self.get_point(x, y) for x in range(length) for y in range(height))
    
    def __repr__(self):
        return self.__class__.__name__ + ('no ' if not self.wraparound else '') + 'wraparound' + ': {}'.format(self.limits)
        

class CircularVision:
    def __init__(self, distance, *, p):
        self.distance = distance
        self.p = p
    
    def get_visible_points(self, grid, position):
        return grid.get_circle(position, self.distance, p=self.p)

        
def test_point():
    p = Point(1, 1)
    d = Direction(2, 3)
    assert p + d == Point(3, 4)
    assert d + d == Direction(4, 6)
    with pytest.raises(TypeError):
        d + p
    with pytest.raises(TypeError):
        p + p
    assert str(p + d) == 'Point: 3, 4'
    
def test_wa_point():
    p = WrapAroundPoint(1, 1, limits=(3, 3))
    d = Direction(2, 3)
    assert p + d == WrapAroundPoint(0, 1, limits=(3, 3))
    with pytest.raises(TypeError):
        d + p
    with pytest.raises(TypeError):
        p + p
    assert str(p + d) == 'WrapAroundPoint: 0, 1'    

def test_square_grid():
    g = SquareGrid(10, 5)
    p = g.get_point(1, 1)
    assert p + g.N * 20 == p
    assert p + g.N * 7 == g.get_point(1, 3)

def test_vision_p0():
    g = SquareGrid(10, 5)
    p = g.get_point(4, 4)
    vision = CircularVision(2, p=0)
    points = vision.get_visible_points(g, p)
    assert set(points) == set(g.get_point(*coords) for coords in [(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4)])
    
def test_vision_p2():
    g = SquareGrid(10, 5)
    p = g.get_point(4, 4)
    vision = CircularVision(2, p=2)
    points = vision.get_visible_points(g, p)
    assert set(points) == set(g.get_point(*coords) for coords in [(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4), (5, 0), (5, 3), (3, 0), (3, 3)])
    vision = CircularVision(20, p=2)
    assert set(vision.get_visible_points(g, p)) == set(g.get_all_points())
