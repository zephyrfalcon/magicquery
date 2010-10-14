# addons.py

def load_addons(filename):
    with open(filename, 'rb') as f:
        lines = filter(None, map(str.strip, f.readlines()))

    cards = {}
    for line in lines:
        if line.startswith('#'):
            continue
        card, sep, data = map(str.strip, line.partition('|'))
        keywords = data.split()
        cards[card] = keywords

    return cards

def proliferate(cards, keywords):
    """ Add keywords to card objects. """
    for cardname, kw in keywords.items():
        for card in cards:
            if card['name'].lower() == cardname.lower():
                card._data['keywords'] = kw
                #print "Added keywords for:", card['name']
