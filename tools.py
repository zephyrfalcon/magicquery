# tools.py

class Null(object):
    def __repr__(self): return "<Null>"
    def __le__(self, other): return False
    def __lt__(self, other): return False
    def __gt__(self, other): return False
    def __ge__(self, other): return False
    def __eq__(self, other): return False
    def __neq__(self, other): return False
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __getitem__(self, name): return self

null = Null()

class Abstract(Null):
    # used to wrap "variable" power/toughness. it should not compare as true
    # to anything, but we should still be able to identify its value and print
    # it.
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)

def contains_any(s, substrs):
    for sub in substrs:
        if sub in s: return True
    return False
