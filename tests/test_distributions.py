import pytest
import context
from distributions import Uniform, SampleWithoutReplacement

def test_uniform():
    d = Uniform(5, 1000, seed=1)
    assert next(d) == 142
    assert next(d) == 587
    d = Uniform(5, 1000, seed=1)
    for x in d:
        assert x == 142
        break

def test_sample_nr():
    d = SampleWithoutReplacement(range(10000), 50, seed=1)
    assert next(d) == 2201
    assert next(d) == 9325
    d = SampleWithoutReplacement(range(10000), 50, seed=1)
    for x in d:
        assert x == 2201
        break
    for x in d:
        assert x == 9325
        break