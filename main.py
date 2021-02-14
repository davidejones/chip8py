# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pyglet
from pyglet import gl

import imgui
# Note that we could explicitly choose to use PygletFixedPipelineRenderer
# or PygletProgrammablePipelineRenderer, but create_renderer handles the
# version checking for us.
from imgui.integrations.pyglet import create_renderer

from buffers import FrameBuffer
from chip8 import Chip8
from debug import DebugScreen
import ctypes

WIDTH = 800
HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FBO = None
texture = None


def main():
    window = pyglet.window.Window(width=800, height=600, resizable=False)

    imgui.create_context()
    impl = create_renderer(window)

    debug = DebugScreen()

    c8 = Chip8()
    c8.load_rom("breakout.rom")

    # Create the framebuffer (rendering target).
    from ctypes import byref, sizeof, POINTER
    #fbo = FrameBuffer()
    #fbo.bind()
    # buf = gl.GLuint(0)
    # gl.glGenFramebuffers(1, byref(buf))
    # gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, buf)
    #
    # # Create the texture (internal pixel data for the framebuffer).
    # tex = gl.GLuint(0)
    # gl.glGenTextures(1, byref(tex))
    # gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, WIDTH, HEIGHT, 0, gl.GL_RGBA, gl.GL_FLOAT, None)
    #
    # # Bind the texture to the framebuffer.
    # gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, tex, 0)
    #
    # gl.glViewport(0, 0, WIDTH, HEIGHT)
    #
    # # DRAW BEGIN
    # gl.glClearColor(0.114, 0.114, 0.114, 1.0)  # 1d1d1d
    # gl.glMatrixMode(gl.GL_PROJECTION)
    # gl.glLoadIdentity()
    # gl.glOrtho(0, 100, 0, 100, -1, 1)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glLoadIdentity()
    # gl.glColor3f(1.0, 1.0, 1.0)
    # label = pyglet.text.Label(
    #     "Hello, World", font_name='Times New Roman', font_size=36,
    #     x=WIDTH / 2, y=HEIGHT / 2, anchor_x='center', anchor_y='center')
    # label.draw()
    # # DRAW END
    #
    # # Something may have gone wrong during the process, depending on the
    # # capabilities of the GPU.
    # res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    # if res != gl.GL_FRAMEBUFFER_COMPLETE:
    #     raise RuntimeError('Framebuffer not completed')

    # create FBO object once
    # FBO = gl.GLuint()
    # gl.glGenFramebuffersEXT(1, ctypes.byref(FBO))
    #
    # # bind the frame buffer
    # gl.glBindFramebufferEXT(gl.GL_FRAMEBUFFER_EXT, FBO)
    #
    # tex = gl.GLuint(0)
    # gl.glGenTextures(1, byref(tex))
    # gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    # gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    # blank = (gl.GLubyte * (WIDTH * HEIGHT * 4))()
    # gl.glTexImage2D(gl.GL_TEXTURE_2D, 0,
    #              gl.GL_RGBA,
    #              WIDTH, HEIGHT,
    #              0,
    #              gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
    #              blank)
    # texture = pyglet.image.Texture(WIDTH, HEIGHT, gl.GL_TEXTURE_2D, tex.value)
    #
    # # bind texture and depth buffer to FBO
    # gl.glBindTexture(texture.target, texture.id)
    # gl.glFramebufferTexture2DEXT(gl.GL_FRAMEBUFFER_EXT, gl.GL_COLOR_ATTACHMENT0_EXT, texture.target, texture.id, 0)
    #
    # # clear FBO and set some GL defaults
    # gl.glEnable(gl.GL_BLEND)
    # gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    # gl.glEnable(gl.GL_DEPTH_TEST)
    # gl.glDepthFunc(gl.GL_LEQUAL)
    # gl.glClearDepth(1.0)
    # gl.glClearColor(0.5, 0.0, 0.5, 0.0)  # set clear color yourself!
    # gl.glViewport(0, 0, texture.width, texture.height)
    # gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    # #SetScreen(0, 0, texture.width, texture.height)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    # gl.glLoadIdentity()
    # gl.glMatrixMode(gl.GL_PROJECTION)
    # gl.glLoadIdentity()
    # gl.glOrtho(0, 0, texture.width, texture.height, -1.0, 1.0)
    # gl.glMatrixMode(gl.GL_MODELVIEW)
    #
    # # simple error checking
    # status = gl.glCheckFramebufferStatusEXT(gl.GL_FRAMEBUFFER_EXT)
    # assert status == gl.GL_FRAMEBUFFER_COMPLETE_EXT

    def update(dt):
        c8.cycle()
        # Start Window
        imgui.new_frame()

        # Draw Menubar
        # if imgui.begin_main_menu_bar():
        #     if imgui.begin_menu("File", True):
        #         clicked_quit, selected_quit = imgui.menu_item(
        #             "Quit", 'Cmd+Q', False, True
        #         )
        #         if clicked_quit:
        #             exit(1)
        #         imgui.end_menu()
        #     imgui.end_main_menu_bar()

        # Draw game window
        #imgui.begin("Game", False, imgui.WINDOW_NO_RESIZE)
        #imgui.set_window_size(64*7, 32*7)
        #imgui.set_window_position(10, 30)
        #imgui.image(tex, WIDTH, HEIGHT)
        #imgui.end()

        debug.update(c8.opcode)

    def draw(dt):
        gl.glClearColor(0.114, 0.114, 0.114, 1.0)  # 1d1d1d
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glBegin(gl.GL_LINES)
        # create a line, x,y,z
        gl.glVertex3f(100.0, 100.0, 0.25)
        gl.glVertex3f(200.0, 300.0, -0.75)
        gl.glEnd()

        update(dt)
        #window.clear()

        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.clock.schedule_interval(draw, 1 / 120.)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()
