"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # 256 in order to 256 bytes of memory
        self.ram = [0] * 256
        # 8 is a general-purpose register, start at index
        self.reg = [0] * 8
        self.pc = 0
        self.sp = 7  # stack pointer starts at top of register
        self.flag = 0b00000000  # set all flags to false upon initiations
        self.running = False
        self.reg[self.sp] = 0xF4  # points to RAM address F4

    def call_stack(self, func):
        branch_table = {
            0b10000010: self.ldi,
            0b01000111: self.prn,
            0b10100010: self.mult,
            0b00000001: self.hlt,
            0b01000101: self.push,
            0b01000110: self.pop,
            0b01010000: self.call,
            0b00010001: self.ret
        }
        if func in branch_table:
            branch_table[func]()
        else:
            print('Not a valid function')
            sys.exit(1)

    # now instruct each command in how to behave
    def ldi(self):
        reg_num = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_num] = value
        self.pc += 3

    def prn(self):
        reg_num = self.ram_read(self.pc + 1)
        print(self.reg[reg_num])
        self.pc += 2

    def mult(self):
        self.alu('mult', self.pc + 1, self.pc + 2)
        self.pc += 3

    def hlt(self):
        self.running = False
        self.pc += 1

    def push(self, value=None):
        self.sp -= 1

        if not value:
            value = self.reg[self.ram_read(self.pc + 1)]

        self.ram_write(value, self.reg[self.sp])
        self.pc += 2

    def pop(self):
        value = self.ram[self.sp]
        self.reg[self.ram[self.pc+1]] = value
        self.sp += 1
        self.pc += 2

    def call(self):
        self.reg[self.sp] -= 1
        self.ram_write(self.reg[self.sp], self.pc + 1)
        self.pc += 2
        self.trace()

    def ret(self):
        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def load(self):
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

        if op == "mult":
            self.reg[self.ram[reg_a]] *= self.reg[self.ram[reg_b]]

        else:
            raise Exception("Unsupported ALU operation")

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

        while self.running:
            ir = self.ram[self.pc]
            self.call_stack(ir)
