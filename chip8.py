import math
import random
from collections import deque
from dataclasses import dataclass
from typing import Callable
import pyglet
from pyglet import shapes
from pyglet.window import key


@dataclass
class OpCode:
    """Class for keeping track of an operation code."""
    bytecode: int = 0
    asm: str = ''
    desc: str = ''
    run: Callable = None


class Chip8(object):
    def __init__(self, scale) -> None:
        super().__init__()
        self.width = 64
        self.height = 32
        self.scale = scale
        self.rom_pointer = 512
        self.memory = bytearray(4096)
        # 0x050-0x0A0 - Used for the built in 4x5 pixel font set (0-F) (80 bytes)
        # We put it into the memory starting from the address 0x0 which is easier for us,
        # but it could be anywhere between 0x00 and 0x1FF because those memory cells are
        # free and we only need 80 of them.
        self.memory[0:80] = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
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
                0x00E0: OpCode(bytecode=0x00E0, asm="CLS", desc="Clear the display.", run=self.cls),
                0x00EE: OpCode(bytecode=0x00EE, asm="RET", desc="Return from a subroutine.", run=self.ret)
            },
            0x1000: OpCode(bytecode=0x1000, asm="JP addr", desc="Jump to location nnn.", run=self.jp),
            0x2000: OpCode(bytecode=0x2000, asm="CALL addr", desc="Call subroutine at nnn.", run=self.call),
            0x3000: OpCode(bytecode=0x3000, asm="SE Vx, byte", desc="Skip instruction if Vx = kk.", run=self.se),
            0x4000: OpCode(bytecode=0x4000, asm="SNE Vx, byte", desc="Skip instruction if Vx != kk", run=self.sne),
            0x5000: OpCode(bytecode=0x5000, asm="SE Vx, Vy", desc="Skip instruction if Vx = Vy", run=self.se2),
            0x6000: OpCode(bytecode=0x6000, asm="LD Vx, byte", desc="Puts value kk into register Vx", run=self.ld),
            0x7000: OpCode(bytecode=0x7000, asm="ADD Vx, byte", desc="Set Vx = Vx + kk.", run=self.add),
            0x8000: {
                0x8000: OpCode(bytecode=0x8000, asm="LD Vx, Vy", desc="Set Vx = Vy.", run=self.ld2),
                0x8001: OpCode(bytecode=0x8001, asm="OR Vx, Vy", desc="Set Vx = Vx OR Vy.", run=self.OR),
                0x8002: OpCode(bytecode=0x8002, asm="AND Vx, Vy", desc="Set Vx = Vx AND Vy.", run=self.AND),
                0x8003: OpCode(bytecode=0x8003, asm="XOR Vx, Vy", desc="Set Vx = Vx XOR Vy.", run=self.XOR),
                0x8004: OpCode(bytecode=0x8004, asm="ADD Vx, Vy", desc="Set Vx = Vx + Vy, set VF = carry.", run=self.add2),
                0x8005: OpCode(bytecode=0x8005, asm="SUB Vx, Vy", desc="Set Vx = Vx - Vy, set VF = NOT borrow.", run=self.sub),
                0x8006: OpCode(bytecode=0x8006, asm="SHR Vx {, Vy}", desc="Set Vx = Vx SHR 1.", run=self.shr),
                0x8007: OpCode(bytecode=0x8007, asm="SUBN Vx, Vy", desc="Set Vx = Vy - Vx", run=self.subn),
                0x800E: OpCode(bytecode=0x800E, asm="SHL Vx {, Vy}", desc="Set Vx = Vx SHL 1.", run=self.shl)
            },
            0x9000: OpCode(bytecode=0x9000, asm="SNE Vx, Vy", desc="Skip instruction if Vx != Vy.", run=self.sne2),
            0xA000: OpCode(bytecode=0xA000, asm="LD I, addr", desc="Set I = nnn.", run=self.ld3),
            0xB000: OpCode(bytecode=0xB000, asm="JP V0, addr", desc="Jump to location nnn + V0.", run=self.jp2),
            0xC000: OpCode(bytecode=0xC000, asm="RND Vx, byte", desc="Set Vx = random byte AND kk.", run=self.rnd),
            0xD000: OpCode(bytecode=0xD000, asm="DRW Vx, Vy, nibble", desc="Display n-byte sprite", run=self.drw),
            0xE000: {
                0xE09E: OpCode(bytecode=0xE09E, asm="SKP Vx", desc="Skip instruction if key in Vx is pressed", run=self.skp),
                0xE0A1: OpCode(bytecode=0xE0A1, asm="SKNP Vx", desc="Skip instruction if key in Vx is not pressed", run=self.sknp)
            },
            0xF000: {
                0xF007: OpCode(bytecode=0xF007, asm="LD Vx, DT", desc="Set Vx = delay timer value.", run=self.ld4),
                0xF00A: OpCode(bytecode=0xF00A, asm="LD Vx, K", desc="Wait for a key press, store key in Vx.", run=self.ld5),
                0xF015: OpCode(bytecode=0xF015, asm="LD DT, Vx", desc="Set delay timer = Vx.", run=self.ld6),
                0xF018: OpCode(bytecode=0xF018, asm="LD ST, Vx", desc="Set sound timer = Vx.", run=self.ld7),
                0xF01E: OpCode(bytecode=0xF01E, asm="ADD I, Vx", desc="Set I = I + Vx.", run=self.add3),
                0xF029: OpCode(bytecode=0xF029, asm="LD F, Vx", desc="Set I = location of sprite for digit Vx.", run=self.ld8),
                0xF033: OpCode(bytecode=0xF033, asm="LD B, Vx", desc="Store BCD representation of Vx in memory locations I, I+1, and I+2.", run=self.ld9),
                0xF055: OpCode(bytecode=0xF055, asm="LD [I], Vx", desc="Store registers V0 through Vx in memory starting at location I.", run=self.ld10),
                0xF065: OpCode(bytecode=0xF065, asm="LD Vx, [I]", desc="Read registers V0 through Vx from memory starting at location I.", run=self.ld11)
            }
        }
        self.grid = []
        for i in range(32):
            line = []
            for j in range(64):
                line.append(0)
            self.grid.append(line)
        self.emptyGrid = self.grid[:]
        self.on_color = [255, 255, 255]
        self.off_color = [0, 0, 0]
        # creating a batch object
        self.batch = pyglet.graphics.Batch()
        self.shape_grid = []
        for i in range(len(self.grid)):
            shape_line = []
            for j in range(len(self.grid[i])):
                shape_line.append(shapes.Rectangle((j * self.scale) + 10, ((32 * 20) - (i * self.scale)) - 20, self.scale, self.scale, color=self.off_color, batch=self.batch))
            self.shape_grid.append(shape_line)
        self.pc_key_map = {
            key._1: 1,
            key._2: 2,
            key._3: 3,
            key._4: 0xc,
            key.Q: 4,
            key.W: 5,
            key.E: 6,
            key.R: 0xd,
            key.A: 7,
            key.S: 8,
            key.D: 9,
            key.F: 0xe,
            key.Z: 0xa,
            key.X: 0,
            key.C: 0xb,
            key.V: 0xf
        }
        self.keyboard_keys = []
        for i in range(0, 16):
            self.keyboard_keys.append(False)
        self.is_paused = False
        self.sample_instructions = deque()
        self.sample_instructions_size = 12

    def reset(self):
        """
        Returns variables to initial state for game reload
        """
        self.cls(None)
        self.pc = 0x200  # Program counter starts at 0x200
        self.opcode = 0  # Reset current opcode
        self.index_register = bytearray(0)  # Reset index register
        self.registers = list(map(lambda x: 0, self.registers))
        self.stack = []
        self.keyboard_keys = list(map(lambda x: False, self.keyboard_keys))
        self.sample_instructions.clear()

    def get_instruction(self, opcode):
        """
        Takes an opcode and looks up the appropriate instruction
        :param opcode:
        :return: instruction
        """
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
        return ret

    def key_press(self, symbol):
        """
        Takes a computer key char and sets the equivalent chip8 key to true
        :param symbol:
        """
        if symbol in self.pc_key_map:
            chip8_key = self.pc_key_map[symbol]
            self.keyboard_keys[chip8_key] = True

    def key_release(self, symbol):
        """
        Takes a computer key char and sets the equivalent chip8 key to false
        :param symbol:
        """
        if symbol in self.pc_key_map:
            chip8_key = self.pc_key_map[symbol]
            self.keyboard_keys[chip8_key] = False

    def cls(self, opcode):
        """
        00E0 - CLS, Clear the display.
        """
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                self.grid[i][j] = 0
        for i in range(len(self.shape_grid)):
            for j in range(len(self.shape_grid[i])):
                self.shape_grid[i][j].color = self.off_color

    def ret(self, opcode):
        """
        00EE - RET, Return from a subroutine.
        The interpreter sets the program counter to the address at the top of the stack & subtracts 1 from stack pointer
        """
        val = self.stack.pop()
        self.pc = val

    def jp(self, opcode):
        """
        1nnn - JP addr, Jump to location nnn.
        The interpreter sets the program counter to nnn
        :param opcode:
        """
        self.pc = (opcode & 0x0FFF) - 2 # sub 2 as we add 2 at end of all ops

    def call(self, opcode):
        """
        2nnn - CALL addr, Call subroutine at nnn.
        The interpreter increments the stack pointer, then puts the current PC on the top of the stack. PC is set to nnn
        :param opcode:
        """
        # store in stack too?
        self.stack.append(self.pc)
        self.pc = (opcode & 0x0FFF) - 2 # sub 2 as we add 2 at end of all ops

    def se(self, opcode):
        """
        3xkk - SE Vx, byte, Skip next instruction if Vx = kk.
        The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = opcode & 0x00FF
        if self.registers[vx] == vy:
            self.pc += 2

    def sne(self, opcode):
        """
        4xkk - SNE Vx, byte, Skip next instruction if Vx != kk.
        The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
        :param opcode:
        """
        n = (opcode & 0x0F00) >> 8
        target = opcode & 0x00FF
        if self.registers[n] != target:
            self.pc += 2

    def se2(self, opcode):
        """
        5xy0 - SE Vx, Vy, Skip next instruction if Vx = Vy.
        The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4

        if self.registers[vx] == self.registers[vy]:
            self.pc += 2

    def ld(self, opcode):
        """
        6xkk - LD Vx, byte, Set Vx = kk.
        The interpreter puts the value kk into register Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        nn = opcode & 0x00FF
        self.registers[vx] = nn

    def add(self, opcode):
        """
        7xkk - ADD Vx, byte, Set Vx = Vx + kk.
        Adds the value kk to the value of register Vx, then stores the result in Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        kk = opcode & 0x00FF
        self.registers[vx] = self.registers[vx] + kk

    def ld2(self, opcode):
        """
        8xy0 - LD Vx, Vy, Set Vx = Vy.
        Stores the value of register Vy in register Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vy]

    def OR(self, opcode):
        """
        8xy1 - OR Vx, Vy, Set Vx = Vx OR Vy.
        Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx.
        A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the
        result is also 1. Otherwise, it is 0.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] | self.registers[vy]

    def AND(self, opcode):
        """
        8xy2 - AND Vx, Vy, Set Vx = Vx AND Vy.
        Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx.
        A bitwise AND compares the corrseponding bits from two values, and if both bits are 1,
        then the same bit in the result is also 1. Otherwise, it is 0.
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] & self.registers[vy]

    def XOR(self, opcode):
        """
        8xy3 - XOR Vx, Vy, Set Vx = Vx XOR Vy.
        Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx.
        An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same,
        then the corresponding bit in the result is set to 1. Otherwise, it is 0.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[vx] = self.registers[vx] ^ self.registers[vy]

    def add2(self, opcode):
        """
        8xy4 - ADD Vx, Vy, Set Vx = Vx + Vy, set VF = carry.
        The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1,
        otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        self.registers[vx] += self.registers[vy]

        # catch overflow
        if self.registers[vx] > 0xFF:
            self.registers[0xF] = 1

    def sub(self, opcode):
        """
        8xy5 - SUB Vx, Vy, Set Vx = Vx - Vy, set VF = NOT borrow.
        If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        # catch underflow
        if self.registers[vx] > self.registers[vy]:
            self.registers[0xF] = 1

        self.registers[vx] -= self.registers[vy]

    def shr(self, opcode):
        """
        8xy6 - SHR Vx {, Vy}, Set Vx = Vx SHR 1.
        If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[vx] & 0x1
        self.registers[vx] >>= 1

    def subn(self, opcode):
        """
        8xy7 - SUBN Vx, Vy, Set Vx = Vy - Vx, set VF = NOT borrow.
        If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        self.registers[0xF] = 0

        # catch underflow
        if self.registers[vx] > self.registers[vy]:
            self.registers[0xF] = 1

        self.registers[vx] = self.registers[vy] - self.registers[vx]

    def shl(self, opcode):
        """
        8xyE - SHL Vx {, Vy}, Set Vx = Vx SHL 1.
        If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        self.registers[0xF] = self.registers[vx] & 0x80
        self.registers[vx] <<= 1

    def sne2(self, opcode):
        """
        9xy0 - SNE Vx, Vy, Skip next instruction if Vx != Vy.
        The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4

        if self.registers[vx] != self.registers[vy]:
            self.pc += 2

    def ld3(self, opcode):
        """
        Annn - LD I, addr, Set I = nnn.
        The value of register I is set to nnn.
        :param opcode:
        """
        addr = opcode & 0x0FFF
        self.index_register = addr

    def jp2(self, opcode):
        """
        Bnnn - JP V0, addr, Jump to location nnn + V0.
        The program counter is set to nnn plus the value of V0.
        :rtype: object
        """
        addr = opcode & 0x0FFF
        self.pc = self.registers[0] + addr - 2 # sub 2 as we add 2 at end of all ops

    def rnd(self, opcode):
        """
        Cxkk - RND Vx, byte, Set Vx = random byte AND kk.
        The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk.
        The results are stored in Vx. See instruction 8xy2 for more information on AND.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        vy = opcode & 0x00FF

        rand = random.randint(0, 255)

        self.registers[vx] = vy & rand

    def drw(self, opcode):
        """
        Dxyn - DRW Vx, Vy, nibble, Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed
        as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any
        pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is
        outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction
        8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen & sprites.
        :rtype: object
        """
        vx = (opcode & 0x0F00) >> 8
        vy = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F

        addr = self.index_register
        sprite = self.memory[addr:addr + n]

        if self.draw(self.registers[vx], self.registers[vy], sprite):
            self.registers[0xf] = 1
        else:
            self.registers[0xf] = 0

    def set_grid_colors(self):
        """
        sets the grid colors
        """
        for i in range(len(self.shape_grid)):
            for j in range(len(self.shape_grid[i])):
                if self.grid[i][j] == 1:
                    self.shape_grid[i][j].color = self.off_color
                else:
                    self.shape_grid[i][j].color = self.on_color

    def draw(self, vx, vy, sprite):
        """
        Called from drw builds out the render grid and sets the colors
        """
        collision = False
        for i, byte in enumerate(sprite):
            for j, bit in enumerate(list(bin(byte)[2:].zfill(8))):
                try:
                    if self.grid[vy + i][vx + j] == 1 and int(bit) == 1:
                        collision = True
                    self.grid[vy + i][vx + j] = self.grid[vy + i][vx + j] ^ int(bit)
                except IndexError:
                    continue
        self.set_grid_colors()
        return collision

    def skp(self, opcode):
        """
        Ex9E - SKP Vx, Skip next instruction if key with the value of Vx is pressed.
        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position,
        PC is increased by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        chip8_key = self.registers[vx]
        if self.keyboard_keys[chip8_key]:
            self.pc += 2

    def sknp(self, opcode):
        """
        ExA1 - SKNP Vx, Skip next instruction if key with the value of Vx is not pressed.
        Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position,
        PC is increased by 2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        chip8_key = self.registers[vx]
        if not self.keyboard_keys[chip8_key]:
            self.pc += 2

    def ld4(self, opcode):
        """
        Fx07 - LD Vx, DT, Set Vx = delay timer value.
        The value of DT is placed into Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        self.registers[vx] = 0 # read from a real timer?

    def ld5(self, opcode):
        """
        Fx0A - LD Vx, K, Wait for a key press, store the value of the key in Vx.
        All execution stops until a key is pressed, then the value of that key is stored in Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        active_key = None

        while True:
            if any(self.keyboard_keys):
                active_keys = [index for index, val in enumerate(self.keyboard_keys) if val]
                active_key = active_keys[0] if active_keys else None
                break

        self.registers[vx] = active_key

    def ld6(self, opcode):
        """
        Fx15 - LD DT, Vx, Set delay timer = Vx.
        DT is set equal to the value of Vx.
        :param opcode:
        """
        # delay_timer(Vx)
        vx = (opcode & 0x0F00) >> 8
        val = self.registers[vx]
        #self.delayTimer.setTimer(value)

    def ld7(self, opcode):
        """
        Fx18 - LD ST, Vx, Set sound timer = Vx.
        ST is set equal to the value of Vx.
        :param opcode:
        """
        # sound_timer(Vx)
        vx = (opcode & 0x0F00) >> 8
        value = self.registers[vx]
        #self.soundTimer.setTimer(value)

    def add3(self, opcode):
        """
        Fx1E - ADD I, Vx, Set I = I + Vx.
        The values of I and Vx are added, and the results are stored in I.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        self.index_register += self.registers[vx]

    def ld8(self, opcode):
        """
        Fx29 - LD F, Vx, Set I = location of sprite for digit Vx.
        The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        val = self.registers[vx]
        self.index_register = val * 5

    def ld9(self, opcode):
        """
        Fx33 - LD B, Vx, Store BCD representation of Vx in memory locations I, I+1, and I+2.
        The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I,
        the tens digit at location I+1, and the ones digit at location I+2.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        value = str(self.registers[vx])

        fillNum = 3 - len(value)
        value = '0' * fillNum + value

        for i in range(len(value)):
            self.memory[self.index_register + i] = int(value[i])

    def ld10(self, opcode):
        """
        Fx55 - LD [I], Vx, Store registers V0 through Vx in memory starting at location I.
        The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        for i in range(0, vx + 1):
            self.memory[self.index_register + i] = self.registers[i]

    def ld11(self, opcode):
        """
        Fx65 - LD Vx, [I], Read registers V0 through Vx from memory starting at location I.
        The interpreter reads values from memory starting at location I into registers V0 through Vx.
        :param opcode:
        """
        vx = (opcode & 0x0F00) >> 8
        for i in range(0, vx + 1):
            self.registers[i] = self.memory[self.index_register + i]

    def load_rom(self, path_to_rom):
        """
        Opens the rom file and loads it into memory
        :param path_to_rom:
        """
        ptr = self.rom_pointer
        with open(path_to_rom, 'rb') as f:
            while True:
                byte = f.read(1)
                if not byte:
                    break
                self.memory[ptr:ptr + 1] = [int.from_bytes(byte, "big", signed=False)]
                ptr += 1

    def cycle(self, force=False):
        """
        executing chip8 cpu cycles
        Takes the current instructution and runs it
        """
        if not self.is_paused or force:
            # Fetch opcode
            opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

            # lookup instruction to run and execute
            self.opcode = self.get_instruction(opcode)
            if len(self.sample_instructions) > self.sample_instructions_size:
                self.sample_instructions.popleft()
            self.sample_instructions.append(self.opcode)
            self.opcode.run(opcode)
            self.pc += 2

    def render(self):
        """
        Call the pyglet batch render for rendering all the shapes
        """
        self.batch.draw()

