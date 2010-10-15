# magicquery.py
#
# TODO: remove ugly globals etc; needs reorganized and refactored

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

# TODO: expand this so it shows all relevant info for a card
def show_card(name):
    for card in cards:
        if card['name'].lower() == name.strip().lower():
            print card['name']
            print card['manacost']
            print card['type_oracle']
            print card['rules_oracle']
            if card['power'] is not null:
                print "%s/%s" % (card['power'], card['toughness'])
            break

def mainloop():
    while 1:
        try:
            line = raw_input("> ")
        except EOFError:
            print; break

        if line.startswith("?"):
            show_card(line[1:].strip())
            continue

        for card in cards:
            try:
                result = eval(line, globals(), card)
            except:
                continue # ignore for now
            if result:
                print card['name']
        
if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "", [])

    cards = load_cards(sets=args)
    if addondir:
        load_addons(sets=args)
    mainloop()

                
