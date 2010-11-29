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

def unique(lst, key=None, keep=None):
    """ Take a list and return a new list with duplicate elements removed.
        Preserves the original order.
        By default, the value of the items themselves are used to determine
        duplicates, but a function <key> may be specified to do this instead
        (for example, lambda c: c['name'] would produce a list unique by card
        name).
        In case a duplicate is found, the <keep> function may be used to
        determine which one is kept; it takes two items and returns a boolean;
        if true, the first one is kept, otherwise the second.
    """
    if key is None: key = lambda x: x
    if keep is None: keep = lambda a, b: a
    d = {}
    for idx, item in enumerate(lst):
        dkey = key(item)
        try:
            existing = d[dkey]
        except KeyError:
            d[dkey] = (idx, item)
        else:
            if not keep(existing, item):
                d[dkey] = item

    results = d.values()
    results.sort()
    return [x[1] for x in results]

