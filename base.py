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
        
    def get_circle(self, position, radius):
        # must avoid repeating the same point twice (not just performance, but semantics)
        circle = set()
        for delta_x in range(-radius, radius+1):
            for delta_y in range(-radius, radius+1):
                if delta_x ** 2 + delta_y ** 2 <= radius ** 2:
                    circle.add(position + delta_x * self.E + delta_y * self.N)
        return circle
    
    def get_all_points(self):
        length, height = self.limits
        return (self.get_point(x, y) for x in range(length) for y in range(height))
    
    def __repr__(self):
        return self.__class__.__name__ + ('no ' if not self.wraparound else '') + 'wraparound' + ': {}'.format(self.limits)
        

# feels like this should belong inside Grid, or CircleVision should also be taken out 
class PrincipalDirectionVision:
    def __init__(self, distance):
        self.distance = distance
    
    def get_visible_points(self, grid, position):
        visible_points = {position}
        for direction in grid.PRINCIPAL_DIRECTIONS:
            for d in range(1, self.distance+1):
                visible_points.add(position + d * direction)
        return visible_points
                
                
class CircleVision:
    def __init__(self, distance):
        self.distance = distance
    
    def get_visible_points(self, grid, position):
        return grid.get_circle(position, self.distance)

        
def test_point():
    p = Point(1, 1)
    d = Direction(2, 3)
    assert p + d == Point(3, 4)
    assert d + d == Direction(4, 6)
    with pytest.raises(TypeError):
        d + p
        p + p
    assert str(p + d) == 'Point: 3, 4'
    
def test_wa_point():
    p = WrapAroundPoint(1, 1, limits=(3, 3))
    d = Direction(2, 3)
    assert p + d == WrapAroundPoint(0, 1, limits=(3, 3))
    with pytest.raises(TypeError):
        d + p
        p + p
    assert str(p + d) == 'WrapAroundPoint: 0, 1'    

def test_square_grid():
    g = SquareGrid(10, 5)
    p = g.get_point(1, 1)
    assert p + g.N * 20 == p
    assert p + g.N * 7 == g.get_point(1, 3)

def test_pd_vision():
    g = SquareGrid(10, 5)
    p = g.get_point(4, 4)
    vision = PrincipalDirectionVision(2)
    points = vision.get_visible_points(g, p)
    assert set(points) == set(g.get_point(*coords) for coords in [(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4)])
    
def test_circle_vision():
    g = SquareGrid(10, 5)
    p = g.get_point(4, 4)
    vision = CircleVision(2)
    points = vision.get_visible_points(g, p)
    assert set(points) == set(g.get_point(*coords) for coords in [(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4), (5, 0), (5, 3), (3, 0), (3, 3)])
    vision = CircleVision(20)
    assert set(vision.get_visible_points(g, p)) == set(g.get_all_points())
