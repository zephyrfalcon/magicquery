# tools.py

class Null(object):
    def __repr__(self): return "<Null>"
    def __lt__(self, other): return False
    def __gt__(self, other): return False
    def __eq__(self, other): return False
    def __nonzero__(self): return False
    def __getattr__(self, name): return self
    def __getitem__(self, name): return self

null = Null()

