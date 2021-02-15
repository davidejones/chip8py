import imgui


class DebugScreen(object):

    def update(self, opcode=None, registers=None, index_register=None):
        # Draw general information
        imgui.begin("Debug", False, imgui.WINDOW_NO_RESIZE)
        imgui.set_window_size(320, 550)
        imgui.set_window_position(470, 30)
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

        imgui.end()

    def render(self):
        pass
