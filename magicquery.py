# magicquery.py

import getopt
import readline
import sys
#
import addons
import cardloader
import magiccard
import magiccarddb

def mainloop(cards):
    db = magiccarddb.MagicCardDB(cards)

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

    loader = cardloader.CardLoader(sets=args)
    loader.load_cards()
    loader.load_addons()

    mainloop(loader.cards)

                
