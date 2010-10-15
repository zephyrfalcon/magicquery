# magiccard.py

from tools import null

CARD_ATTRS = ['name', 'artist', 'multiverseid', 'number', 'rarity', 
              'type_oracle', 'rules_printed', 'type_printed', 'rules_oracle',
              'manacost', 'power', 'toughness', 'flavor_text']

class DataConverter:
    
    def convert(self, name, node, value):
        method_name = "do_" + name
        f = getattr(self, method_name, None)
        if f:
            return f(node, value)
        else:
            return value

    def do_number(self, node, value):
        try:
            return int(value)
        except:
            return null

    def do_power(self, node, value):
        try:
            return int(value)
        except:
            return value # probably '*'

    do_toughness = do_power

    def do_manacost(self, node, value):
        parts = []
        for n in node.findall('symbol'):
            parts.append(n.text)
        return parts


class MagicCard(object):

    def __init__(self):
        self._data = {}
        self._dc = DataConverter()

    @classmethod
    def from_xml(cls, xml):
        c = cls()
        for name in CARD_ATTRS:
            node = xml.find(name)
            if node is not None:
                value = xml.find(name)
                value = c._dc.convert(name, node, value.text)
                c._data[name] = value
            else:
                c._data[name] = null
        c._post_process()
        return c

    def _post_process(self):
        # add some attributes that make certain queries easier.
        before, sep, after = self._data['type_oracle'].partition("--")
        self._data['_types'] = before.lower().strip().split()
        self._data['_subtypes'] = after.lower().strip().split()

    def __getitem__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return getattr(self, name) # for properties

    def type(self, name):
        return name.lower() in self._data['_types']

    def subtype(self, name):
        return name.lower() in self._data['_subtypes']

    def anytype(self, name):
        return self.type(name) or self.subtype(name)

    @property
    def colorless(self):
        for x in self._data['manacost']:
            if x.startswith(("{", "R", "B", "W", "G", "U")):
                return False
        return True

    def name_like(self, s):
        return s.lower() in self['name'].lower()
    def flavor_like(self, s):
        return s.lower() in self['flavor_text'].lower()
    def text_like(self, s):
        return s.lower() in self['rules_oracle'].lower()

    def has(self, keyword):
        for kw in self['keywords']:
            parts = kw.split(':')
            if parts[0] == keyword: return True
        return False

    def grants(self, keyword):
        for kw in self['keywords']:
            if kw.startswith('>'):
                parts = kw[1:].split(':')
                if parts[0] == keyword: return True
        return False

    # TODO: maybe_has or something, for ?keywords

    def protection(self, x):
        for kw in self['keywords']:
            parts = kw.split(":")
            if parts[0] == "protection" and x == parts[1]:
                return True
        return False

#
# set color properties dynamically

COLORS = [('red', 'R'), ('white', 'W'), ('blue', 'U'), ('green', 'G'),
          ('black', 'B')]
def add_color_property(color, symbol):
    f = lambda self: symbol in self._data['manacost']
    f.__name__ = color
    setattr(MagicCard, color, property(f))
for color, symbol in COLORS:
    add_color_property(color, symbol)

