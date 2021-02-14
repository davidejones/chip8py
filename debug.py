import imgui


class DebugScreen(object):

    def update(self, opcode=None):
        # Draw general information
        imgui.begin("Debugger", False, imgui.WINDOW_NO_RESIZE)
        imgui.set_window_size(320, 550)
        imgui.set_window_position(470, 30)
        imgui.text("CPU:")
        imgui.same_line()
        imgui.text_colored("Eggs", 0.2, 1., 0.)

        imgui.text("Current Instruction:")
        imgui.same_line()
        if opcode:
            imgui.text_colored(opcode.asm or 'Unknown', 0.2, 1., 0.)
        else:
            imgui.text_colored('Unknown', 0.2, 1., 0.)
        imgui.end()

    def render(self):
        pass
