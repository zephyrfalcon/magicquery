# magicquery.py
#
# TODO: remove ugly globals etc

import ConfigParser
import getopt
import os
import readline
import sys
import time
import xml.etree.ElementTree as ET
#
import magiccard

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

def extract_data(xml):
    setnode = xml.find('set')
    cards = xml.findall('set/cards/card')
    return setnode, cards

def determine_xml_files(sets):
    xmlfiles = os.listdir(xmldir)
    xmlfiles = [fn for fn in xmlfiles if fn.endswith(".xml")]
    if sets:
        xmlfiles = [fn for fn in xmlfiles if os.path.splitext(fn)[0] in sets]
    xmlfiles = [os.path.join(xmldir, fn) for fn in xmlfiles]
    return xmlfiles

def load_cards(sets=[]):
    xmlfiles = determine_xml_files(sets)
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

def mainloop():
    while 1:
        try:
            line = raw_input("> ")
        except EOFError:
            break

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
    mainloop()

                
