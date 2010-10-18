# magicquery.py
#
# TODO: remove ugly globals etc; needs reorganized and refactored

import __builtin__
import ConfigParser
import getopt
import os
import readline
import sys
import time
import xml.etree.ElementTree as ET
#
import addons
import magiccard
from tools import null

class MagicSet(object):

    @classmethod
    def from_xml(cls, xml):
        s = cls()
        for name in ['name', 'shortname', 'release_date']:
            setattr(s, name, xml.find(name).text)
        return s

def extract_data(xml):
    setnode = xml.find('set')
    cards = xml.findall('set/cards/card')
    return setnode, cards

def get_files_for_sets(sets, dir, suffix):
    files = os.listdir(dir)
    files = [fn for fn in files if fn.endswith(suffix)]
    if sets:
        files = [fn for fn in files if os.path.splitext(fn)[0] in sets]
    files = [os.path.join(dir, fn) for fn in files]
    return files

class CardLoader:

    def __init__(self, sets=None):
        self.cfg = self._read_configuration()
        self.sets = sets or []
        self.cards = []

    def _read_configuration(self):
        cp = ConfigParser.ConfigParser()
        cp.read("config.txt")
        return cp

    def load_cards(self):
        xmldir = os.path.expanduser(self.cfg.get('main', 'xmldir'))
        xmlfiles = get_files_for_sets(self.sets, xmldir, ".xml")
        t1 = time.time()
        for fn in xmlfiles:
            print "Loading:", fn
            x = ET.parse(fn)
            setnode, cardnodes = extract_data(x)
            theset = MagicSet.from_xml(setnode)
            cs = [magiccard.MagicCard.from_xml(cardnode) for cardnode in cardnodes]
            for c in cs: c._data['set'] = theset
            self.cards.extend(cs)
        t2 = time.time()
        print "%d cards in %d files, loaded in %.2fs" % (len(self.cards),
              len(xmlfiles), t2-t1)

        return self.cards

    def load_addons(self):
        addondir = os.path.expanduser(self.cfg.get('main', 'addondir'))
        if addondir:
            addon_files = get_files_for_sets(self.sets, addondir, ".txt")
            for fn in addon_files:
                keywords = addons.load_addons(fn)
                addons.proliferate(self.cards, keywords) # :-)

def mana_cost_repr(card):
    return "".join(["{%s}" % x for x in card['manacost']])

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
    if card['power'] is not null:
        print "%s/%s" % (card['power'], card['toughness'])

def mainloop(cards):
    db = MagicCardDB(cards)

    while 1:
        try:
            line = raw_input("> ")
        except EOFError:
            print; break

        if line.startswith("?"):
            db.show_card(line[1:].strip())
            continue

        db.query(line)
        db.show_results()

        
if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "", [])

    loader = CardLoader(sets=args)
    loader.load_cards()
    loader.load_addons()

    mainloop(loader.cards)

                
