class Atom:
    def __init__(self, x=0, y=0, name='Atom'):
        self.name = name
        self._x = x
        self._y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, new):
        self._x = new

    @y.setter
    def y(self, new):
        self._y = new

    def __sub__(self, new):
        self.x -= new.x
        self.y -= new.y
        return self

    def __add__(self, new):
        self.x += new.x
        self.y += new.y
        return self

    def __repr__(self):
        return f"{self.name}(x={self.x}, y={self.y})"


class Rectangle(Atom):
    def __init__(self, x, y, name):
        super().__init__(x, y, name)
        '''
        x = Atom(20, 30, 'Point')
        y = Atom(40, 50, 'Point')
        '''

    def bbox(self):
        x = self.x
        y = self.y
        return x.x, x.y, y.x, y.y

    def isNull(self):
        if 'none' in [self.x, self.y]:
            return True
        else:
            return False
