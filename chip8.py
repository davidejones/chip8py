import random
from dataclasses import dataclass
from typing import Callable


@dataclass
class OpCode:
    """Class for keeping track of an operation code."""
    bytecode: int = 0
    asm: str = ''
    description: str = ''
    run: Callable = None


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
        self.registers = [0 for x in range(16)]
        self.stack = []
        self.instructions = {
            0x0000: {
                0x00E0: OpCode(bytecode=0x00E0, asm="CLS", description="Clear the display.", run=self.cls),
                0x00EE: OpCode(bytecode=0x00EE, asm="RET", description="Return from a subroutine. The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.", run=self.ret)
            },
            0x1000: OpCode(bytecode=0x1000, asm="JP addr", description="Jump to location nnn. The interpreter sets the program counter to nnn.", run=self.jp),
            0x2000: OpCode(bytecode=0x2000, asm="CALL addr", description="Call subroutine at nnn. The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.", run=self.call),
            0x3000: OpCode(bytecode=0x3000, asm="SE Vx, byte", description="Skip next instruction if Vx = kk. The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.", run=self.se),
            0x4000: OpCode(bytecode=0x4000, asm="SNE Vx, byte", description="Skip next instruction if Vx != kk.  The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.", run=self.sne),
            0x5000: OpCode(bytecode=0x5000, asm="SE Vx, Vy", description="Skip next instruction if Vx = Vy.The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.", run=self.se2),
            0x6000: OpCode(bytecode=0x6000, asm="LD Vx, byte", description="The interpreter puts the value kk into register Vx.", run=self.ld),
            0x7000: OpCode(bytecode=0x7000, asm="ADD Vx, byte", description="Set Vx = Vx + kk. Adds the value kk to the value of register Vx, then stores the result in Vx.", run=self.add),
            0x8000: {
                0x8000: OpCode(bytecode=0x8000, asm="LD Vx, Vy", description="Set Vx = Vy.Stores the value of register Vy in register Vx.", run=self.ld2),
                0x8001: OpCode(bytecode=0x8001, asm="OR Vx, Vy", description="Set Vx = Vx OR Vy. Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.", run=self.OR),
                0x8002: OpCode(bytecode=0x8002, asm="AND Vx, Vy", description="Set Vx = Vx AND Vy. Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0.", run=self.AND),
                0x8003: OpCode(bytecode=0x8003, asm="XOR Vx, Vy", description="Set Vx = Vx XOR Vy. Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.", run=self.XOR),
                0x8004: OpCode(bytecode=0x8004, asm="ADD Vx, Vy", description="Set Vx = Vx + Vy, set VF = carry. The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.", run=self.add2),
                0x8005: OpCode(bytecode=0x8005, asm="SUB Vx, Vy", description="Set Vx = Vx - Vy, set VF = NOT borrow.If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.", run=self.sub),
                0x8006: OpCode(bytecode=0x8006, asm="SHR Vx {, Vy}", description="Set Vx = Vx SHR 1.If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.", run=self.shr),
                0x8007: OpCode(bytecode=0x8007, asm="SUBN Vx, Vy", description="Set Vx = Vy - Vx, set VF = NOT borrow.If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.", run=self.subn),
                0x800E: OpCode(bytecode=0x800E, asm="SHL Vx {, Vy}", description="Set Vx = Vx SHL 1. If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.", run=self.shl)
            },
            0x9000: OpCode(bytecode=0x9000, asm="SNE Vx, Vy", description="Skip next instruction if Vx != Vy. The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.", run=self.sne2),
            0xA000: OpCode(bytecode=0xA000, asm="LD I, addr", description="Set I = nnn. The value of register I is set to nnn.", run=self.ld3),
            0xB000: OpCode(bytecode=0xB000, asm="JP V0, addr", description="Jump to location nnn + V0. The program counter is set to nnn plus the value of V0.", run=self.jp2),
            0xC000: OpCode(bytecode=0xC000, asm="RND Vx, byte", description="Set Vx = random byte AND kk.The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.", run=self.rnd),
            0xD000: OpCode(bytecode=0xD000, asm="DRW Vx, Vy, nibble", description="Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction 8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen and sprites.", run=self.drw),
            0xE000: {
                0xE09E: OpCode(bytecode=0xE09E, asm="SKP Vx", description="Skip next instruction if key with the value of Vx is pressed. Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.", run=self.skp),
                0xE0A1: OpCode(bytecode=0xE0A1, asm="SKNP Vx", description="Skip next instruction if key with the value of Vx is not pressed. Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.", run=self.sknp)
            },
            0xF000: {
                0xF007: OpCode(bytecode=0xF007, asm="LD Vx, DT", description="Set Vx = delay timer value.The value of DT is placed into Vx.", run=self.ld4),
                0xF00A: OpCode(bytecode=0xF00A, asm="LD Vx, K", description="Wait for a key press, store the value of the key in Vx.All execution stops until a key is pressed, then the value of that key is stored in Vx.", run=self.ld5),
                0xF015: OpCode(bytecode=0xF015, asm="LD DT, Vx", description="Set delay timer = Vx.DT is set equal to the value of Vx.", run=self.ld6),
                0xF018: OpCode(bytecode=0xF018, asm="LD ST, Vx", description="Set sound timer = Vx.ST is set equal to the value of Vx.", run=self.ld7),
                0xF01E: OpCode(bytecode=0xF01E, asm="ADD I, Vx", description="Set I = I + Vx.The values of I and Vx are added, and the results are stored in I.", run=self.add3),
                0xF029: OpCode(bytecode=0xF029, asm="LD F, Vx", description="Set I = location of sprite for digit Vx. The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.", run=self.ld8),
                0xF033: OpCode(bytecode=0xF033, asm="LD B, Vx", description="Store BCD representation of Vx in memory locations I, I+1, and I+2. The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.", run=self.ld9),
                0xF055: OpCode(bytecode=0xF055, asm="LD [I], Vx", description="Store registers V0 through Vx in memory starting at location I. The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.", run=self.ld10),
                0xF065: OpCode(bytecode=0xF065, asm="LD Vx, [I]", description="Read registers V0 through Vx from memory starting at location I. The interpreter reads values from memory starting at location I into registers V0 through Vx.", run=self.ld11)
            }
        }

    def get_instruction(self, opcode):
        ret = None
        try:
            lookup_code = opcode & 0xF000
            ret = self.instructions[lookup_code]
            if isinstance(ret, dict):
                if lookup_code == 0x0000 or lookup_code == 0xE000 or lookup_code == 0xF000:
                    # last 2 digits match
                    last = opcode & 0xF0FF
                    ret = ret[last]
                elif lookup_code == 0x8000:
                    # last digit match
                    last = opcode & 0xF00F
                    ret = ret[last]
        except KeyError:
            print(f'Unknown opcode 0x{opcode:x}')
            #ret = self.noop
        return ret

    def nop(self, *args, **kwargs):
        pass

    def cls(self, opcode):
        pass

    def ret(self, opcode):
        val = self.stack.pop()
        self.pc = val

    def jp(self, opcode):
        self.pc = (opcode & 0x0FFF) - 2 # sub 2 as we add 2 at end of all ops

    def call(self, opcode):
        # store in stack too?
        self.stack.append(self.pc)
        self.pc = (opcode & 0x0FFF) - 2 # sub 2 as we add 2 at end of all ops

    def se(self, opcode):
        # Skip next instruction if Vx = kk.
        # The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
        vx = (opcode & 0x0F00) >> 8
        vy = opcode & 0x00FF
        if self.registers[vx] == vy:
            self.pc += 2

    def sne(self, opcode):
        # Skip next instruction if Vx != kk.
        # The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
        n = (opcode & 0x0F00) >> 8
        target = opcode & 0x00FF
        if self.registers[n] != target:
            self.pc += 2

    def se2(self, opcode):
        # Skip next instruction if Vx = Vy.
        # The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4

        if self.registers[vx] == self.registers[vy]:
            self.pc += 2

    def ld(self, opcode):
        # Vx = NN
        vx = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        self.registers[vx] = nn

    def add(self, opcode):
        # Set Vx = Vx + kk.
        # Adds the value kk to the value of register Vx, then stores the result in Vx.
        vx = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF
        self.registers[vx] = self.registers[vx] + kk

    def ld2(self, opcode):
        # 8xy0 - LD Vx, Vy
        # Set Vx = Vy.
        #
        # Stores the value of register Vy in register Vx.
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vy]

    def OR(self, opcode):
        # 8xy1 - OR Vx, Vy
        # Set Vx = Vx OR Vy.
        #
        # Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] | self.registers[vy]

    def AND(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] & self.registers[vy]

    def XOR(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] ^ self.registers[vy]

    def add2(self, opcode):
        # Vx += Vy
        # Set Vx = Vx + Vy, set VF = carry.
        # The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        self.registers[vx] += self.registers[vy]

        # catch overflow
        if self.registers[vx] > 0xFF:
            self.registers[0xF] = 1

    def sub(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        # catch underflow
        if self.registers[vx] > self.registers[vy]:
            self.registers[0xF] = 1

        self.registers[vx] -= self.registers[vy]

    def shr(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[vx] & 0x1
        self.registers[vx] >>= 1

    def subn(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        # catch underflow
        if self.registers[vx] > self.registers[vy]:
            self.registers[0xF] = 1

        self.registers[vx] = self.registers[vy] - self.registers[vx]

    def shl(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[vx] & 0x80
        self.registers[vx] <<= 1

    def sne2(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4

        if self.registers[vx] != self.registers[vy]:
            self.pc += 2

    def ld3(self, opcode):
        addr = opcode & 0x0FFF
        self.index_register = addr

    def jp2(self, opcode):
        addr = opcode & 0x0FFF
        self.pc = self.registers[0] + addr - 2 # sub 2 as we add 2 at end of all ops

    def rnd(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        vy = opcode & 0x00FF

        rand = random.randint(0, 255)

        self.registers[vx] = vy & rand

    def drw(self, opcode):
        # TODO setup later
        pass

    def skp(self, opcode):
        # Ex9E - SKP Vx
        # Skip next instruction if key with the value of Vx is pressed.
        # Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.
        vx = (opcode & 0x0F00) >> 8
        key = self.registers[vx]
        # TODO if key is down then inc pc
        # if self.keyboardKeys[key]:
        #    self.pc += 2

    def sknp(self, opcode):
        # Skip next instruction if key with the value of Vx is not pressed.
        # Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.
        vx = (opcode & 0x0F00) >> 8
        key = self.registers[vx]
        # TODO if not pressed in pc by 2

    def ld4(self, opcode):
        # Set Vx = delay timer value.
        # The value of DT is placed into Vx.
        vx = (opcode & 0x0F00) >> 8
        self.registers[vx] = 0 # read from a real timer?

    def ld5(self, opcode):
        # Wait for a key press, store the value of the key in Vx.
        # All execution stops until a key is pressed, then the value of that key is stored in Vx.
        pass

    def ld6(self, opcode):
        # delay_timer(Vx)
        vx = (opcode & 0x0F00) >> 8
        val = self.registers[vx]
        #self.delayTimer.setTimer(value)

    def ld7(self, opcode):
        # sound_timer(Vx)
        vx = (opcode & 0x0F00) >> 8
        value = self.registers[vx]
        #self.soundTimer.setTimer(value)

    def add3(self, opcode):
        # Set I = I + Vx.
        # The values of I and Vx are added, and the results are stored in I.
        vx = (opcode & 0x0F00) >> 8
        self.index_register += self.registers[vx]

    def ld8(self, opcode):
        # Set I = location of sprite for digit Vx.
        # The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.
        vx = (opcode & 0x0F00) >> 8
        val = self.registers[vx]
        self.index_register = val * 5

    def ld9(self, opcode):
        # Store BCD representation of Vx in memory locations I, I+1, and I+2.
        # The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.
        vx = (opcode & 0x0F00) >> 8
        value = str(self.registers[vx])

        fillNum = 3 - len(value)
        value = '0' * fillNum + value

        for i in range(len(value)):
            self.memory[self.index_register + i] = int(value[i])

    def ld10(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        for i in range(0, vx + 1):
            self.memory[self.index_register + i] = self.registers[i]

    def ld11(self, opcode):
        vx = (opcode & 0x0F00) >> 8
        for i in range(0, vx + 1):
            self.registers[i] = self.memory[self.index_register + i]

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
        #print(hex(opcode), f'0x{opcode & 0xF000:x}')

        # lookup instruction to run and execute
        self.opcode = self.get_instruction(opcode)
        self.opcode.run(opcode)
        #print(self.opcode)
        self.pc += 2

        print(hex(opcode), self.pc)
