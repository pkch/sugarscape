import random

class Distribution:
    def __init__(self, seed):
        if seed is None:
            self.rng = random
        else:
            self.rng = random.Random()
        self.rng.seed(seed)

    def __iter__(self):
        return self

class Uniform(Distribution):
    def __init__(self, a, b, seed=None):
        '''Uniform a <= x <= b
        '''
        super().__init__(seed)
        self.a = a
        self.b = b

    def __next__(self):
        return self.rng.randint(self.a, self.b)

class SampleWithoutReplacement(Distribution):
    def __init__(self, population, k, seed=None):
        '''Sample of size k from population without replacement
        '''
        super().__init__(seed)
        self._result = self.rng.sample(population, k)
        self.i = -1

    # if we just define __iter__ as yield from self._result, the loop would always start from the beginning (making this a container rather than iterator)
    # also, we wouldn't be able to say next()
    # a single loop would still work perfectly fine (because it automatically obtains iterator iter())
    def __next__(self):
        self.i += 1
        return self._result[self.i]
