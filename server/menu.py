from PIL import Image



class NesMenu(object):

    games = [{'name': 'Super Mario', 'image_fn': 'super-mario-bros.png', 'value': 'local-roms/Super Mario Bros. (JU) (PRG0) [!].nes'},
             {'name': 'Tetris', 'image_fn': 'tetris.png', 'value': 'local-roms/Tetris (U) [!].nes'},
             {'name': 'Zelda', 'image_fn': 'zelda.png', 'value': 'local-roms/Legend of Zelda, The (U) (PRG1).nes'}]
    #         {'name': 'Mario', 'image_fn': 'mario-bros.png', 'value': 'local-roms/Mario Bros. (JU) [!].nes'},


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


    def current_game(self):
        return self.games[self.selected]['value']

    def get_image(self):
        if not('image' in self.games[self.selected]):
            img = Image.open(self.games[self.selected]['image_fn'])
            self.games[self.selected]['image'] = img.resize((57, 45), Image.ANTIALIAS)

        # TODO: add arrows...

        return self.games[self.selected]['image']

