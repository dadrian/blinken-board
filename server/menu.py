from PIL import Image
from PIL import ImageDraw



class NesMenu(object):

    games = [{'name': 'Super Mario', 'image_fn': 'images/super-mario-bros.png', 'value': 'local-roms/Super Mario Bros. (JU) (PRG0) [!].nes'},
             {'name': 'Tetris', 'image_fn': 'images/tetris.png', 'value': 'local-roms/Tetris (U) [!].nes'},
             {'name': 'Pacman', 'image_fn': 'images/pacman.png', 'value': 'local-roms/Pac-Man (U) [!].nes'},
             {'name': 'Donkey Kong', 'image_fn': 'images/donkey-kong.png', 'value': 'local-roms/Donkey Kong (JU).nes'}]
    #         {'name': 'Mario', 'image_fn': 'mario-bros.png', 'value': 'local-roms/Mario Bros. (JU) [!].nes'},


    def __init__(self):
        self.selected = 0
        self.fill = 0
        self.fill_dir = 12

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

        img = self.games[self.selected]['image']

        arrows = Image.new("RGBA", (57, 45))

        # add arrows...
        a = self.fill
        self.fill += self.fill_dir
        if self.fill > 255 or self.fill < 0:
            self.fill_dir = -self.fill_dir
            self.fill += self.fill_dir

        draw = ImageDraw.Draw(arrows, mode='RGBA')
        r, g, b = (255, 255, 0)
        draw.line((50,22, 55,27), fill=(r, g, b, a), width=3)
        draw.line((50,32, 55,27), fill=(r, g, b, a), width=3)

        draw.line((7,22, 2,27), fill=(r, g, b, a), width=3)
        draw.line((7,32, 2,27), fill=(r, g, b, a), width=3)

        return Image.alpha_composite(img, arrows)
