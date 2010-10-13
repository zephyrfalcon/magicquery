# magicquery.py

import ConfigParser
import getopt
import os
import readline
import sys
import time
import xml.etree.ElementTree as ET
#
import magiccard

DEBUG = 1

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

xmlfiles = [os.path.join(xmldir, fn) for fn in os.listdir(xmldir)
            if fn.endswith(".xml")]

if DEBUG: xmlfiles = xmlfiles[:3]

def extract_data(xml):
    setnode = xml.find('set')
    cards = xml.findall('set/cards/card')
    return setnode, cards

cards = []
t1 = time.time()
for fn in xmlfiles:
    print fn
    x = ET.parse(fn)
    setnode, cardnodes = extract_data(x)
    theset = MagicSet.from_xml(setnode)
    cs = [magiccard.MagicCard.from_xml(cardnode) for cardnode in cardnodes]
    for c in cs: c._data['set'] = theset
    cards.extend(cs)
    print len(cards)
t2 = time.time()
print t2-t1

# On iMac G5 1.8GHz, loading the XML takes ~20s... but this is WITHOUT
# creating card objects etc. WITH creating them, it's about ~30s.

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

    mainloop()

                
