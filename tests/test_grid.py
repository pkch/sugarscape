import pytest
import context
from grids import SquareGrid, CircularVision

def test_square_grid():
    g = SquareGrid(3, 3)
    assert str(g) == 'SquareGrid wraparound: 3 x 3'
    p = (1, 1)
    d = (2, 3)
    assert g.move(p, d, 1) == (0, 1)
    g = SquareGrid(10, 5)
    p = (1, 1)
    assert g.move(p, g.N, 20) == p
    assert g.move(p, g.N, 7) == (1, 3)

def test_square_grid_nowrap():
    g = SquareGrid(3, 3, wraparound=False)
    p = (1, 1)
    d = (2, 3)
    assert g.move(p, d, 1) is None
    g = SquareGrid(10, 5, wraparound=False)
    p = (1, 1)
    assert g.move(p, g.N, 20) is None
    assert g.move(p, g.N, 3) == (1, 4)

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
