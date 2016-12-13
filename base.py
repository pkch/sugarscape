import pytest

class SquareGrid:
    N = (0, 1)
    E = (1, 0)
    S = (0, -1)
    W = (-1, 0)
    PRINCIPAL_DIRECTIONS = (N, E, S, W)
    def __init__(self, length, height, wraparound=True):
        self.length = length
        self.height = height
        self.wraparound = wraparound

    def get_circle(self, center, radius, p):
        # must avoid repeating the same point twice (not just performance, but semantics)
        circle = set()

        if p == 0:
            circle.add(center)
            for direction in self.PRINCIPAL_DIRECTIONS:
                for d in range(1, radius+1):
                    point = self.move(center, direction, d)
                    circle.add(point)
        else:
            for delta_x in range(-radius, radius+1):
                for delta_y in range(-radius, radius+1):
                    if p == float('inf') or delta_x ** p + delta_y ** p <= radius ** p:
                        direction = delta_x, delta_y
                        point = self.move(center, self.E, delta_x)
                        point = self.move(point, self.N, delta_y)
                        circle.add(point)

        return circle

    def is_inside(self, coords):
        x, y = coords
        return 0 <= x < self.length and 0 <= y < self.height

    def move(self, start_coords, direction, distance):
        x, y = start_coords
        dx, dy = direction
        x += dx * distance
        y += dy * distance
        if self.wraparound:
            return x % self.length, y % self.height
        else:
            if self.is_inside((x, y)):
                return x, y
            else:
                return None

    def get_all_points(self):
        return ((x, y) for x in range(self.length) for y in range(self.height))

    def __repr__(self):
        return self.__class__.__name__ + ('no ' if not self.wraparound else '') + 'wraparound' + ': {} x {}'.format(self.length, self.height)

class CircularVision:
    def __init__(self, distance, *, p):
        self.distance = distance
        self.p = p

    def get_visible_points(self, grid, position):
        return grid.get_circle(position, self.distance, p=self.p)


def test_wa_point():
    g = SquareGrid(3, 3)
    p = (1, 1)
    d = (2, 3)
    assert g.move(p, d, 1) == (0, 1)

def test_square_grid():
    g = SquareGrid(10, 5)
    p = (1, 1)
    assert g.move(p, g.N, 20) == p
    assert g.move(p, g.N, 7) == (1, 3)

def test_vision_p0():
    g = SquareGrid(10, 5)
    p = (4, 4)
    vision = CircularVision(2, p=0)
    points = vision.get_visible_points(g, p)
    assert set(points) == set([(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4)])

def test_vision_p2():
    g = SquareGrid(10, 5)
    p = (4, 4)
    vision = CircularVision(2, p=2)
    points = vision.get_visible_points(g, p)
    assert set(points) == set([(4, 4), (4, 0), (4, 1), (4, 3), (4, 2), (5, 4), (6, 4), (3, 4), (2, 4), (5, 0), (5, 3), (3, 0), (3, 3)])
    vision = CircularVision(20, p=2)
    assert set(vision.get_visible_points(g, p)) == set(g.get_all_points())
