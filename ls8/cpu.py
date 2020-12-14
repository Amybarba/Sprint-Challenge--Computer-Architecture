"""CPU functionality."""

import sys
import time


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # 256 in order to 256 bytes of memory
        self.ram = [0] * 256
        # 8 is a general-purpose register, start at index
        self.reg = [0] * 8
        self.pc = self.reg[0]
        self.sp = 7  # stack pointer starts at top of register
        self.fl = 0b00000000  # set all flags to false upon initiations
        self.running = False
        self.reg[self.sp] = 0xF4  # points to RAM address F4
        self.im = 5
        self.isr = 6
        self._init_non_alu_opcodes_()

    def _init_non_alu_opcodes_(self):
        self.branch_table = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mult,
            0b00000001: self.hlt,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret,
            0b01010010: self.int,
            0b00010011: self.iret,
            0b01010101: self.jeq,
            0b01011010: self.jge,
            0b01010111: self.jgt,
            0b01011001: self.jle,
            0b01011000: self.jlt,
            0b01010100: self.jmp,
            0b01010110: self.jne,
            0b10000011: self.ld,
            0b00000000: self.nop,
            0b01001000: self.pra,
            0b10000100: self.st
        }

    # now map the alu op codes to each command
    ALU = {
        0b10100000: 'add',
        0b10101000: 'and',
        0b10100111: 'cmp',
        0b01100110: 'dec',
        0b10100011: 'div',
        0b01100101: 'inc',
        0b10100100: 'mod',
        0b10100010: 'mul',
        0b01101001: 'not',
        0b10101010: 'or',
        0b10101100: 'shl',
        0b10101101: 'shr',
        0b10100001: 'sub',
        0b10101011: 'xor',
    }
    # now map the alu commands to the operations(op)
    alu_op = {
        'add': lambda x, y: x + y,
        'and': lambda x, y: x & y,
        'cmp': lambda x, y: 1 if x == y else 2 if x > y else 4,
        'dec': lambda x, y: x - 1,
        'div': lambda x, y: x // y,
        'inc': lambda x, y: x + 1,
        'mod': lambda x, y: x % y,
        'mul': lambda x, y: x * y,
        'not': lambda x, y: ~x,
        'or': lambda x, y: x | y,
        'shl': lambda x, y: x << y,
        'shr': lambda x, y: x >> y,
        'sub': lambda x, y: x - y,
        'xor': lambda x, y: x ^ y,
    }

    # now instruct each command in how to behave
    def ldi(self):
        self.reg[self.operand_a] = self.operand_b

    def prn(self):
        print(self.reg[self.operand_a])

    def mult(self):
        self.alu('mult', self.pc + 1, self.pc + 2)
        self.pc += 3

    def hlt(self):
        self.running = False

    def push(self, value=None):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.reg[self.operand_a])

    def pop(self):
        value = self.ram[self.sp]
        self.reg[self.ram[self.pc + 1]] = value
        self.sp += 1
        self.pc += 2

    def call(self):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.pc + 1)
        self.pc = self.reg[self.operand_a]

    def ret(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def int(self):
        self.reg[self.isr] != (1 << self.reg[self.operand_a])
        self.pc += 1

    def iret(self):
        for i in range(6, -1, -1):
            self.reg[i] = self.ram_read(self.reg[self.sp])
            self.reg[self.sp] += 1
        # flags
        self.fl = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        # program counter
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1
        # allow interrupts
        self.reg[self.im] = self.old_im

    def jeq(self):
        if self.fl & 0b1:
            self.pc = self.reg[self.operand_a]
        else:
            self.pc += 1

    def jge(self):
        if self.fl & 0b11:
            self.pc = self.reg[self.operand_a]
        else:
            self.pc += 1

    def jgt(self):
        if self.fl & 0b10:
            self.pc = self.reg[self.operand_a]
        else:
            self.pc += 1

    def jle(self):
        if self.fl & 0b101:
            self.pc = self.rg[self.operand_a]
        else:
            self.pc += 1

    def jlt(self):
        if self.fl & 0b100:
            self.pc = self.re[self.operand_a]
        else:
            self.pc += 1

    def jmp(self):
        self.pc = self.reg[self.operand_a]

    def jne(self):
        if not self.fl & 0b1:
            self.pc = self.reg[self.operand_a]
        else:
            self.pc += 1

    def ld(self):
        self.reg[self.operand_a] = self.ram_read(sefl.reg[self.operand_b])

    def pra(self):
        print(chr(self.reg[self.operand_a]), end='', flush=True)

    def st(self):
        self.ram_write(self.reg[self.operand_a], self.reg[self.operand_b])

    def nop(self):
        pass

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self, file_path):
        """Load a program into memory."""
        file_path = sys.argv[1]
        program = open(f"{file_path}", "r")
        address = 0

        for line in program:

            if line[0] == "0" or line[0] == "1":
                command = line.split("#", 1)[0]
                self.ram[address] = int(command, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        try:
            x = self.reg[reg_a]
            y = self.reg[reg_b] if reg_b is not None else None
            result = self.alu_op[op](x, y)

            if op == "cmp":
                self.fl = result
            else:
                self.reg[reg_a] = result
                self.reg[reg_b] &= 0xFF

        except Exception:
            raise SystemError("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        old_time = new_time = time.time()

        while self.running:
            ir = self.reg[self.im]
            self.check_inter()

            new_time = time.time()
            if new_time - old_time > 1:
                self.reg[self.isr] |= 0b00000001
                old_time = new_time

            # start instruction reg and ops
            self.ir = self.ram_read(self.pc)
            if self.ir & 0b100000 > 0:
                # for an alu operation
                self.alu(self.ALU[self.ir], self.operand_a, self.operand_b)
            else:
                # for a non alu operation
                self.branch_table[self.ir]()
            # if it does not modify program counter
            if self.ir & 0b10000 == 0:
                # go to next
                self.pc += 1

    def check_inter(self):
        interrupts = self.reg[self.im] & self.reg[self.isr]
        for interrupt in range(8):
            bit = 1 << interrupt
            # if it triggers interrupt
            if interrupts & bit:
                # keep memory of old state
                self.old_im = self.reg[self.im]
                # stop interrupts
                self.reg[self.im] = 0
                
