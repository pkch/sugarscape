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

    def get_circle(self, center, radius, *, p):
        # must avoid repeating the same point twice (not just performance, but semantics)
        circle = set()

        if p == 0:
            circle.add(center)
            for direction in self.PRINCIPAL_DIRECTIONS:
                for d in range(1, radius+1):
                    point = self.move(center, direction, d)
                    circle.add(point)
        else:
            max_distance = radius ** p
            for delta_x in range(-radius, radius+1):
                for delta_y in range(-radius, radius+1):
                    if p != float('inf'):
                        distance = delta_x ** p + delta_y ** p
                        if distance > max_distance:
                            continue
                    direction = delta_x, delta_y
                    point = self.move(center, self.E, delta_x)
                    point = self.move(point, self.N, delta_y)
                    circle.add(point)

        return circle

    def distance(self, p1, p2, *, p=2):
        return sum((c1 - c2) ** p for c1, c2 in zip(p1, p2)) ** (1/p)

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
        return self.__class__.__name__ + (' no' if not self.wraparound else '') + ' wraparound' + ': {} x {}'.format(self.length, self.height)


class CircularVision:
    def __init__(self, distance, *, p):
        self.distance = distance
        self.p = p

    def get_visible_points(self, grid, position):
        return grid.get_circle(position, self.distance, p=self.p)

