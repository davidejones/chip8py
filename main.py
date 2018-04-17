import pyglet


class Chip8(object):
    def __init__(self) -> None:
        super().__init__()

    def draw(self):
        pass

    def cycle(self):
        pass


def main():
    window = pyglet.window.Window()

    c8 = Chip8()
    c8.cycle()
    c8.draw()

    pyglet.app.run()


if __name__ == '__main__':
    main()
