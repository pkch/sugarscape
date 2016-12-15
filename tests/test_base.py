import pytest
import context

from agents import largest_values

def test_largest_values():
    assert largest_values([1, 2, 3, 4], key=lambda x: x%2) == [1, 3]
    assert largest_values([1, 2, 3, 4], key=lambda x: (x%2,)) == [1, 3]
