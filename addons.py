# addons.py

def load_addons(filename):
    print "Loading keywords for:", filename
    with open(filename, 'rb') as f:
        lines = filter(None, map(str.strip, f.readlines()))

    cards = {}
    for line in lines:
        if line.startswith('#'):
            continue
        card, sep, data = map(str.strip, line.partition('|'))
        card = card.lower()
        keywords = data.split()
        cards[card] = keywords

    return cards

def proliferate(cards, keywords):
    """ Add keywords to card objects. """
    for card in cards:
        name = card['name'].lower()
        try:
            kw = keywords[name]
            card._data['keywords'] = kw
        except KeyError:
            continue

    '''
    for cardname, kw in keywords.items():
        for card in cards:
            if card['name'].lower() == cardname.lower():
                card._data['keywords'] = kw
                #print "Added keywords for:", card['name']
    '''

