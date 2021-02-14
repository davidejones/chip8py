from instructions import Instructions


class Chip8(object):
    def __init__(self) -> None:
        super().__init__()
        self.rom_pointer = 512
        self.memory = bytearray(4096)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F) (80 bytes)
        # We put it into the memory starting from the adress 0x0 which is easier for us,
        # but it could be anywhere between 0x00 and 0x1FF because those memory cells are free and we only need 80 of them.
        self.memory[80:160] = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 86
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        self.pc = 0x200  # Program counter starts at 0x200
        self.opcode = 0  # Reset current opcode
        self.index_register = bytearray(0)  # Reset index register
        self.registers = [bytearray(0) for x in range(8)]
        self.stack = []
        self.instructions = Instructions(self.pc, self.stack, self.registers, self.index_register)

    def load_rom(self, name):
        ptr = self.rom_pointer
        with open(name, 'rb') as f:
            while True:
                byte = f.read(1)
                if not byte:
                    break
                self.memory[ptr:ptr + 1] = [int.from_bytes(byte, "big", signed=False)]
                ptr += 1

    def draw(self):
        pass

    def cycle(self):
        # Fetch opcode
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        print(opcode, f'0x{opcode & 0xF000:x}', hex(opcode & 0xF000))

        # lookup instruction to run and execute
        self.opcode = self.instructions[opcode]
        #operation.run(self.opcode)
        print(self.opcode)

        #self.instructions[opcode]
        self.pc += 2
