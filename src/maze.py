class Pac_gum:
    def __init__(self, x: int, y: int, rect):
        self.x = x
        self.y = y
        self.rect = rect
        self.eat = False


class Super_pac_gum(Pac_gum):
    def __init__(self, x: int, y: int, rect):
        super().__init__(x, y, rect)


class Cell:
    def __init__(self, x: int, y: int, value: int, i: int, j: int):
        self.x = x
        self.y = y
        self.value = value
        self.pac_g = None
        self.pos = [i, j]
