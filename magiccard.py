# magiccard.py

import re
import tools

CARD_ATTRS = ['name', 'artist', 'multiverseid', 'number', 'rarity', 
              'type_oracle', 'rules_printed', 'type_printed', 'rules_oracle',
              'manacost', 'power', 'toughness', 'flavor_text', 'loyalty']

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
            return tools.null

    do_loyalty = do_number # only for Planeswalkers

    def do_power(self, node, value):
        try:
            return int(value)
        except:
            return tools.Abstract(value) # probably '*'

    do_toughness = do_power

    def do_manacost(self, node, value):
        parts = []
        for n in node.findall('symbol'):
            parts.append(n.text)
        return parts

class MagicSet(object):

    @classmethod
    def from_xml(cls, xml):
        s = cls()
        for name in ['name', 'shortname', 'release_date']:
            setattr(s, name, xml.find(name).text)

        s.tags = []
        tag_node = xml.find('tags')
        if tag_node:
            for child in tag_node.getchildren():
                s.tags.append(child.tag)

        return s

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
                c._data[name] = tools.null
        c._post_process()
        return c

    def _post_process(self):
        # add some attributes that make certain queries easier.
        before, sep, after = self._data['type_oracle'].partition("--")
        self._data['_types'] = before.lower().strip().split()
        self._data['_subtypes'] = after.lower().strip().split()

        # do the same thing for the printed rules/types, so we can find e.g.
        # interrupts or type 'Falcon'
        typep = self._data['type_printed']
        if ' - ' in typep:
            before, sep, after = typep.partition(" - ")
        else:
            before, sep, after = typep.partition("--")
        self._data['_printed_types'] = before.lower().strip().split()
        self._data['_printed_subtypes'] = after.lower().strip().split()

    def __getitem__(self, name):
        try:
            return self._data[name]
        except KeyError:
            try:
                return getattr(self, name) # for properties
            except AttributeError:
                # we need to raise a KeyError here so eval() tries to look the
                # name up in the global namespace next
                raise KeyError, name

    def type(self, name):
        return name.lower() in self._data['_types']

    def subtype(self, name):
        return name.lower() in self._data['_subtypes']

    def anytype(self, name):
        return self.type(name) or self.subtype(name)

    # we support old-school types as well
    def printed_type(self, name):
        return name.lower() in self._data['_printed_types']
    def printed_subtype(self, name):
        return name.lower() in self._data['_printed_subtypes']

    def has_color(self, color):
        for x in self._data['manacost']:
            if tools.contains_any(x, color): return True
        return False

    @property
    def colorless(self):
        if self._data['name'] in force_color['colorless']: 
            return True
        for x in self._data['manacost']:
            if tools.contains_any(x, "RBWGU"):
                return False
        return True

    @property
    def multicolor(self):
        colors_found = 0
        for color in "RBWGU":
            if self.has_color(color): colors_found += 1
        return colors_found > 1

    def name_like(self, s):
        return s.lower() in self['name'].lower()
    def flavor_like(self, s):
        return s.lower() in self['flavor_text'].lower()
    def text_like(self, s):
        return s.lower() in self['rules_oracle'].lower()
    def printed_text_like(self, s):
        return s.lower() in self._data['rules_printed'].lower()

    def name_match(self, regex, case_sensitive=1):
        return re.search(regex, self['name'], 0 if case_sensitive else re.I)
    def flavor_match(self, regex, case_sensitive=1):
        return re.search(regex, self['flavor_text'], 
               0 if case_sensitive else re.I)
    def text_match(self, regex, case_sensitive=1):
        return re.search(regex, self['rules_oracle'], 
               0 if case_sensitive else re.I)
    def printed_text_match(self, regex, case_sensitive=1):
        return re.search(regex, self._data['rules_printed'], 
               0 if case_sensitive else re.I)

    def has(self, keyword, arg=None):
        # E.g. has('protection')
        #      has('protection', 'white')

        for kw in self['keywords']:
            parts = kw.split(':')
            if parts[0] == keyword: 
                if arg is None:
                    return True
                else:
                    if parts[1:] and parts[1].lower() == arg.lower():
                        return True
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

    @property
    def has_hybrid_mana(self):
        for x in self._data['manacost']:
            if len(x) == 2 and (x[0] in "WUGBR" or x[1] in "WUGBR"):
                return True
        return False

    @property
    def power_varies(self):
        return isinstance(self['power'], tools.Abstract)

    @property
    def toughness_varies(self):
        return isinstance(self['toughness'], tools.Abstract)

    @property
    def cmc(self):
        cmc = 0
        for x in self._data['manacost']:
            if x in "RUWGBS":
                cmc += 1
            elif x in "XYZ":
                pass # counts as zero
            elif len(x) == 2 and x[0] == "2" and x[1] in "WURGB":
                cmc += 2 # {2R} etc counts as 2
            elif len(x) == 2 and x[0] in "WURGB" and x[1] in "WURGB":
                cmc += 1 # hybrid mana
            else:
                try:
                    cmc += int(x)
                except:
                    pass
        return cmc

#
# some cards have a color but no mana cost

force_color = {
    'B': ['Slaughter Pact',
          'Living End'],
    'G': ["Summoner's Pact",
          "Dryad Arbor",
          "Hypergenesis"],
    'R': ['Pact of the Titan',
          'Crimson Kobolds', 
          'Crookshank Kobolds', 
          'Kobolds of Kher Keep'],
    'U': ['Pact of Negation',
          'Evermind',
          'Ancestral Vision'],
    'W': ['Intervention Pact',
          'Restore Balance'],
    'colorless': ["Ghostfire"],
}

#
# set color properties dynamically

COLORS = [('red', 'R'), ('white', 'W'), ('blue', 'U'), ('green', 'G'),
          ('black', 'B')]
def add_color_property(color, symbol):
    def f(self):
        return self.has_color(symbol) or self['name'] in force_color[symbol]
    f.__name__ = color
    setattr(MagicCard, color, property(f))
for color, symbol in COLORS:
    add_color_property(color, symbol)

#
# ditto for selected types

TYPE_PROPERTIES = ["creature", "artifact", "instant", "land", "enchantment",
                   "planeswalker", "sorcery"]
def add_type_property(prop):
    def f(self):
        return self.type(prop)
    f.__name__ = prop
    setattr(MagicCard, prop, property(f))
for prop in TYPE_PROPERTIES:
    add_type_property(prop)

