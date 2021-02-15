import imgui


class DebugScreen(object):

    def update(self, opcode=None, registers=None, index_register=None, on_color=(255, 255, 255), off_color=(0, 0, 0)):
        # Draw general information
        imgui.begin("Debug", False, imgui.WINDOW_NO_RESIZE)
        imgui.set_window_size(320, 550)
        imgui.set_window_position(670, 10)
        # imgui.text("CPU:")
        # imgui.same_line()
        # imgui.text_colored("Eggs", 0.2, 1., 0.)

        imgui.text("Registers:")
        if registers:
            imgui.columns(4, "Bar")
            imgui.separator()

            for count, reg in enumerate(registers):
                imgui.text(f'r{count} = 0x{reg:x}')
                imgui.next_column()

            imgui.columns(1)
            imgui.separator()

        imgui.text("Index Register:")
        imgui.same_line()
        if index_register:
            imgui.text_colored(f'0x{index_register:x}', 0.2, 1., 0.)
        else:
            imgui.text_colored(f'Unknown', 0.2, 1., 0.)

        imgui.text("Current Instruction:")
        imgui.same_line()
        if opcode:
            imgui.text_colored(opcode.asm or 'Unknown', 0.2, 1., 0.)
        else:
            imgui.text_colored('Unknown', 0.2, 1., 0.)

        _, color1 = imgui.color_edit3("Color 1", *on_color)
        _, color2 = imgui.color_edit3("Color 2", *off_color)

        imgui.end()

        return color1, color2

