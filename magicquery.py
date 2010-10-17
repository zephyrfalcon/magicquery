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

cp = ConfigParser.ConfigParser()
cp.read("config.txt")
xmldir = os.path.expanduser(cp.get('main', 'xmldir'))
addondir = os.path.expanduser(cp.get('main', 'addondir'))

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

def load_cards(sets=[]):
    xmlfiles = get_files_for_sets(sets, xmldir, ".xml")
    cards = []
    t1 = time.time()
    for fn in xmlfiles:
        print "Loading:", fn
        x = ET.parse(fn)
        setnode, cardnodes = extract_data(x)
        theset = MagicSet.from_xml(setnode)
        cs = [magiccard.MagicCard.from_xml(cardnode) for cardnode in cardnodes]
        for c in cs: c._data['set'] = theset
        cards.extend(cs)
    t2 = time.time()
    print "%d cards in %d files, loaded in %.2fs" % (len(cards),
          len(xmlfiles), t2-t1)

    return cards

def load_addons(sets=[]):
    addon_files = get_files_for_sets(sets, addondir, ".txt")
    for fn in addon_files:
        keywords = addons.load_addons(fn)
        addons.proliferate(cards, keywords) # :-)

def mana_cost_repr(card):
    return "".join(["{%s}" % x for x in card['manacost']])

class MagicCardDB:

    def __init__(self, cards):
        self.cards = cards
        self.results = [] # current result set

    def query(self, expr):
        self.results = []
        count = 0
        for card in cards:
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

def mainloop():
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

    cards = load_cards(sets=args)
    if addondir:
        load_addons(sets=args)
    mainloop()

                
