class Rectangle(object):
    def __init__(self, width, height):
        self._width = width
        self._height = height


r = Rectangle(5, 6)
print("Width: {:d}".format(r._width))
