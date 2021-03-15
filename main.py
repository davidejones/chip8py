# -*- coding: utf-8 -*-
from __future__ import absolute_import

import imgui
import pyglet
from imgui.integrations.pyglet import create_renderer

from chip8 import Chip8


class MainGame:
    def __init__(self, path_to_rom):
        self.scale = 10
        self.FPS = 300
        self.width = 1000
        self.height = 32 * 20
        self.window = pyglet.window.Window(width=self.width, height=self.height, resizable=False)
        imgui.create_context()
        self.impl = create_renderer(self.window)
        self.c8 = Chip8(self.scale)
        self.c8.load_rom(path_to_rom)

        self.window.on_key_press = self.on_key_press
        self.window.on_key_release = self.on_key_release
        pyglet.clock.schedule_interval(self.on_draw, 1.0 / self.FPS)

    def cleanup(self):
        self.impl.shutdown()

    def debug_ui(self):
        # tell imgui its a new frame
        imgui.new_frame()

        # Draw general information
        imgui.begin("Debug", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE)
        imgui.set_window_size(330, 620)
        imgui.set_window_position(660, 10)

        imgui.text("Registers:")
        if self.c8.registers:
            imgui.columns(8, "Bar")
            # imgui.set_column_offset(1, 20)
            imgui.separator()

            for count, reg in enumerate(self.c8.registers):
                # imgui.text(f'r{count} = 0x{reg:x}')
                imgui.text(f'r{count}')
                imgui.next_column()
                imgui.text_colored(f'0x{reg:x}', 0.2, 1., 0.)
                imgui.next_column()

            imgui.columns(1)
            imgui.separator()

        imgui.text("Index Register:")
        imgui.same_line()
        if self.c8.index_register:
            imgui.text_colored(f'0x{self.c8.index_register:x}', 0.2, 1., 0.)
        else:
            imgui.text_colored(f'Unknown', 0.2, 1., 0.)

        imgui.text("Current Instruction:")
        imgui.same_line()
        if self.c8.opcode:
            imgui.text_colored(self.c8.opcode.asm or 'Unknown', 0.2, 1., 0.)
        else:
            imgui.text_colored('Unknown', 0.2, 1., 0.)

        imgui.separator()
        imgui.text("Actions:")
        if imgui.button("RESET", 100, 30):
            self.c8.reset()
        imgui.same_line()
        if imgui.button("PAUSE", 100, 30):
            self.c8.is_paused = True
        imgui.same_line()
        if imgui.button("RESUME", 100, 30):
            self.c8.is_paused = False

        imgui.separator()
        on_color_changed, color1 = imgui.color_edit3("Color 1", *[x / 255.0 for x in self.c8.on_color])
        off_color_changed, color2 = imgui.color_edit3("Color 2", *[x / 255.0 for x in self.c8.off_color])
        if on_color_changed:
            self.c8.on_color = (round(color1[0] * 255), round(color1[1] * 255), round(color1[2] * 255))
            self.c8.draw(0, 0, [])
        if off_color_changed:
            self.c8.off_color = (round(color2[0] * 255), round(color2[1] * 255), round(color2[2] * 255))
            self.c8.draw(0, 0, [])

        imgui.columns(8, 'fileLlist')
        #imgui.push_style_var(imgui.STYLE_ITEM_SPACING, imgui.Vec2(20, 20))

        imgui.text('1')
        imgui.next_column()
        imgui.text('2')
        imgui.next_column()
        imgui.text('3')
        imgui.next_column()
        imgui.text('4')

        imgui.next_column()
        imgui.text('Q')
        imgui.next_column()
        imgui.text('W')
        imgui.next_column()
        imgui.text('E')
        imgui.next_column()
        imgui.text('R')

        imgui.next_column()
        imgui.text('A')
        imgui.next_column()
        imgui.text('S')
        imgui.next_column()
        imgui.text('D')
        imgui.next_column()
        imgui.text('F')

        imgui.next_column()
        imgui.text('Z')
        imgui.next_column()
        imgui.text('X')
        imgui.next_column()
        imgui.text('C')
        imgui.next_column()
        imgui.text('V')
        #imgui.pop_style_var()
        imgui.columns(1)

        imgui.end()

        imgui.begin("Execution", False, imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_COLLAPSE)
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
        # tell imgui to render
        imgui.render()

    def on_key_press(self, symbol, modifiers):
        self.c8.key_press(symbol)

    def on_key_release(self, symbol, modifiers):
        self.c8.key_release(symbol)

    def on_draw(self, dt):
        # clear the window
        self.window.clear()
        # chip8 clock cycle
        self.c8.cycle()
        # chip8 render
        self.c8.render()
        # render imgui elements
        self.debug_ui()
        self.impl.render(imgui.get_draw_data())


def main():
    game = MainGame("games\\breakout.rom")
    pyglet.app.run()
    game.cleanup()


if __name__ == "__main__":
    main()
