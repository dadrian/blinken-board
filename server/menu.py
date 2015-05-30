from PIL import Image



class NesMenu(object):

    games = [{'name': 'Mario', 'image_fn': 'super-mario-bros.png'},
             {'name': 'Tetris', 'image_fn': 'tetris.png'}]


    def __init__(self):
        self.selected = 0

    def left(self):
        self.selected -= 1
        if self.selected < 0:
            self.selected += len(self.games)

    def right(self):
        self.selected += 1
        if self.selected >= len(self.games):
            self.selected = 0


    def get_image(self):
        if not('image' in self.games[self.selected]):
            self.games[self.selected]['image'] = Image.open(self.games[self.selected]['image_fn'])

        return self.games[self.selected]['image']

