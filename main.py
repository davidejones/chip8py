from chip8 import Chip8
from pyglet.window import key
import sys
import pyglet
pyglet.options['debug_gl'] = True
if sys.platform == 'darwin':
    pyglet.options['shadow_window'] = False # we need this for mac os to be able to grab opengl 3.2
from pyglet.gl import *


class MainGame:
    def __init__(self):
        config = pyglet.gl.Config(double_buffer=True, major_version=3, minor_version=2, forward_compatible=False)
        self.window = pyglet.window.Window(caption='Chip8', config=config, width=1024, height=512, resizable=False, vsync=True)
        glViewport(0, 0, 1024, 512)

        print('OpenGL version:', self.window.context.get_info().get_version())
        print('OpenGL 3.2 support:', self.window.context.get_info().have_version(3, 2))

        self.window_should_close = False
        self.c8 = Chip8()
        self.c8.load_rom("breakout.rom")

        # setup function calls
        self.window.on_key_press = self.on_key_press
        self.window.on_resize = self.on_resize
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    def update(self, dt):
        pass

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            pyglet.app.exit()

    def on_resize(self, width, height):
        pass


if __name__ == '__main__':
    g = MainGame()
    pyglet.app.run()
