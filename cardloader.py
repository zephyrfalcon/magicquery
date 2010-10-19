# cardloader.py

import ConfigParser
import os
import time
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
#
import addons
import magiccard

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
            theset = magiccard.MagicSet.from_xml(setnode)
            cs = [magiccard.MagicCard.from_xml(cardnode) 
                  for cardnode in cardnodes]
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

