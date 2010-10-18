# magiccarddb.py

import sys
#
import tools

class MagicCardDB:

    def __init__(self, cards):
        self.cards = cards
        self.results = [] # current result set

    def query(self, expr):
        self.results = []
        count = 0
        for card in self.cards:
            count += 1
            if count % 100 == 0: sys.stdout.write("."); sys.stdout.flush()
            try:
                result = eval(expr, globals(), card)
            except:
                #import traceback; traceback.print_exc(); break
                continue # ignore for now
            if result:
                self.results.append(card)
        print

    def show_results(self):
        max_len = len(str(len(self.results)))
        temp = "%" + str(max_len) + "d"
        for idx, card in enumerate(self.results):
            print (temp % (idx+1)) + "/" + str(len(self.results)),
            print "[%s] %s" % (card['set'].shortname, card['name']),
            print mana_cost_repr(card)

    def show_card(self, s):
        """ Show the card indicated by string s. If s can be converted to a
            number N, then show the N-th card from the last result set.
            Otherwise, show the first card that has a matching name. """
        card = None

        try:
            num = int(s)
        except ValueError:
            for c in cards:
                if c['name'].lower() == s.strip().lower():
                    card = c; break
        else:
            try:
                card = self.results[num-1]
            except IndexError:
                pass

        if card is not None:
            show_card(card)

def show_card(card):
    print card['name']
    print mana_cost_repr(card)
    print card['type_oracle']
    print card['rules_oracle']
    print card['rarity']
    if card['flavor_text']:
        print card['flavor_text']
    if card['power'] is not tools.null:
        print "%s/%s" % (card['power'], card['toughness'])
    if card['loyalty']:
        print "Loyalty:", card['loyalty']

def mana_cost_repr(card):
    return "".join(["{%s}" % x for x in card['manacost']])


