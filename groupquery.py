# groupquery.py

def groupquery(cards, groupf, accf, acc_default):
    """ Do a query not unlike SQL's GROUP BY. 
        groupf(card) is a function that determines the group.
        accf(card, value) takes a value, computes a new value from the given
        card, and "accumulates" them, returning a new value.
        acc_default is the initial accumulator value.
    """
    groups = {}
    for card in cards:
        group = groupf(card)
        group_val = groups.get(group, acc_default)
        groups[group] = accf(card, group_val)
    return groups

if __name__ == "__main__":

    import sys
    short_sets = sys.argv[1:]
    import magicquery
    cards = magicquery.load_cards(short_sets)

    #
    # example: compute the percentage of artifacts in each set

    def group_by_set(card):
        return card['set'].shortname

    def acc_artifacts(card, (artifacts, total)):
        return (artifacts + int(card.type('artifact')), total+1)

    results = groupquery(cards, group_by_set, acc_artifacts, (0, 0))

    for set, (artifacts, total) in sorted(results.items()):
        print "%s: %d cards, %d artifacts\t=> %4.1f%%" % (set, total,
              artifacts, 100.0 * artifacts / total)

