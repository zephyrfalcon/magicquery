# iconic.py
# Quick & dirty script written in an attempt to determine Magic's "iconic"
# creatures, where iconic is defined as, the creature type shows up a lot. :-)
# 
# Notice the restrict() function below; this can be tweaked to change the
# result sets. For example, to find big iconic creatures, use card['power'] >=
# 4. To include all the small fries like goblins and soldiers and merfolk and
# whatnot, just have it return True. :-)

import os
import sys
whereami = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(".."))

import cardloader
import groupquery
import magicquery
import tools

# load all cards
# expects config.txt in parent directory!
loader = cardloader.CardLoader(sets=sys.argv[1:], path="../config.txt")
cards = loader.load_cards()

# remove duplicates
cards = tools.unique(cards, key=lambda c: c['name'])

# add a restriction: creatures must have power of 4 at least
# change this to change the output! ^_^
def restrict(card):
    return card['power'] >= 4

# only keep mono-color creatures
cards = [c for c in cards
         if c.type('creature') and not (c.multicolor or c.colorless)
         and restrict(c)]

print "Inspecting", len(cards), "mono-colored creatures"

colors = "RWBGU"
types = {}
for color in colors:
    types[color] = {}

# count all the subtypes, by color
for card in cards:
    subtypes = card._data['_subtypes'] # list of subtypes, Oracle version
    for color in colors:
        if card.has_color(color):
            for st in subtypes:
                count = types[color].setdefault(st, 0)
                types[color][st] = count + 1

# print the top N creature types for each color
for color in colors:
    print "COLOR:", color
    results = types[color]
    a = results.items()
    a.sort(key=lambda x: -x[1])
    print a[:10]

