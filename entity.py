class Entity:
    # generic object to represent player, enemies, items, etc
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color

    def move(self, dx, dy):
        # move entity given amount
        self.x += dx
        self.y += dy