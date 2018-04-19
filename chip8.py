class Chip8(object):
    def __init__(self) -> None:
        super().__init__()
        self.ram = [b'\x00'] * 4096
        self.display_buffer = [b'\x00'] * 64 * 32
        self.pc = 512
        self.opcode = b'\x00'

    def load_rom(self, name):
        ptr = 512
        with open(name, 'rb') as f:
            byte = f.read(1)
            while byte:
                self.ram[ptr] = byte
                ptr += 1
                byte = f.read(1)

    def draw(self):
        pass

    def cycle(self):
        pass
