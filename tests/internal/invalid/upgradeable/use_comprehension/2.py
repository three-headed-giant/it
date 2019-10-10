operands = list(map(itemgetter(0), tokens))
unique_operands = set(map(attrgetter("unique_version"), tokens))
