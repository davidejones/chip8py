# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pyglet
from pyglet import gl
from pyglet import shapes

import imgui
# Note that we could explicitly choose to use PygletFixedPipelineRenderer
# or PygletProgrammablePipelineRenderer, but create_renderer handles the
# version checking for us.
from imgui.integrations.pyglet import create_renderer

from buffers import FrameBuffer
from chip8 import Chip8
import ctypes

WIDTH = 800
HEIGHT = 600
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FBO = None
texture = None
FPS = 300
scale = 10


def main():
    window = pyglet.window.Window(width=1000, height=32 * 20, resizable=False)

    imgui.create_context()
    impl = create_renderer(window)

    c8 = Chip8(scale)
    c8.load_rom("Tic-Tac-Toe.ch8")

    def debug_ui():
        # Draw general information
        imgui.begin("Debug", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        imgui.set_window_size(330, 620)
        imgui.set_window_position(660, 10)
        # imgui.text("CPU:")
        # imgui.same_line()
        # imgui.text_colored("Eggs", 0.2, 1., 0.)

        imgui.text("Registers:")
        if c8.registers:
            imgui.columns(4, "Bar")
            imgui.separator()

            for count, reg in enumerate(c8.registers):
                imgui.text(f'r{count} = 0x{reg:x}')
                imgui.next_column()

            imgui.columns(1)
            imgui.separator()

        imgui.text("Index Register:")
        imgui.same_line()
        if c8.index_register:
            imgui.text_colored(f'0x{c8.index_register:x}', 0.2, 1., 0.)
        else:
            imgui.text_colored(f'Unknown', 0.2, 1., 0.)

        imgui.text("Current Instruction:")
        imgui.same_line()
        if c8.opcode:
            imgui.text_colored(c8.opcode.asm or 'Unknown', 0.2, 1., 0.)
        else:
            imgui.text_colored('Unknown', 0.2, 1., 0.)

        imgui.separator()
        imgui.text("Colors:")
        on_color_changed, color1 = imgui.color_edit3("Color 1", *[x / 255.0 for x in c8.on_color])
        off_color_changed, color2 = imgui.color_edit3("Color 2", *[x / 255.0 for x in c8.off_color])
        if on_color_changed:
            c8.on_color = (round(color1[0]*255), round(color1[1]*255), round(color1[2]*255))
            c8.draw(0, 0, [])
        if off_color_changed:
            c8.off_color = (round(color2[0] * 255), round(color2[1] * 255), round(color2[2] * 255))
            c8.draw(0, 0, [])

        imgui.end()

        imgui.begin("Execution", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)
        imgui.set_window_size(640, 290)
        imgui.set_window_position(10, 340)
        imgui.columns(2, 'fileLlist')
        imgui.separator()
        imgui.text("bytecode")
        imgui.next_column()
        imgui.text("instruction")
        imgui.separator()
        imgui.set_column_offset(1, 80)

        for x in range(3):
            imgui.next_column()
            imgui.text('0x0000')
            imgui.next_column()
            imgui.text('LD Vx byte')

            imgui.next_column()
            imgui.text('0xF00F')
            imgui.next_column()
            imgui.text('jp addr')

        selected = [True, False]
        imgui.next_column()
        _, selected[0] = imgui.selectable("0xFFFF", selected[0], imgui.SELECTABLE_SPAN_ALL_COLUMNS)
        imgui.next_column()
        _, selected[1] = imgui.selectable("do byte", selected[1], imgui.SELECTABLE_SPAN_ALL_COLUMNS)
        imgui.set_item_allow_overlap()

        imgui.columns(1)
        imgui.separator()
        imgui.end()

    def on_draw(dt):
        # clear the window
        window.clear()
        c8.cycle()
        c8.render()
        imgui.new_frame()
        debug_ui()
        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.clock.schedule_interval(on_draw, 1.0/FPS)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()
