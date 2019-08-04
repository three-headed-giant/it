def x():
    for x in y:
        yield x


def y():
    for x, y in z:
        yield x, y
