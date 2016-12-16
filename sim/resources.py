

class Sugar:
    NO_GROWTH = lambda a, c: 0
    def __init__(self, amount=0, capacity=0, growth=NO_GROWTH):
        self.amount = amount
        self.capacity = capacity
        self.growth = growth

    def update(self):
        self.amount = min(self.capacity, self.amount + self.growth(self.amount, self.capacity))

    def __lt__(self, other):
        if not isinstance(other, Sugar):
            return TypeError
        return self.amount < other.amount