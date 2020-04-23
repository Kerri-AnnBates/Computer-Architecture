"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8  # R0 - R7
        self.pc = 0
        self.running = True
        self.branchtable = {}
        self.HLT = 0b00000001
        self.LDI = 0b10000010
        self.PRN = 0b01000111
        self.MUL = 0b10100010
        self.PUSH = 0b01000101
        self.POP = 0b01000110
        self.branchtable[self.HLT] = self.handle_halt
        self.branchtable[self.LDI] = self.handle_ldi
        self.branchtable[self.PRN] = self.handle_print
        self.branchtable[self.PUSH] = self.handle_push
        self.branchtable[self.POP] = self.handle_pop
        self.SP = 7
        self.reg[self.SP] = 0xF4

    def load(self):
        """Load a program into memory."""

        address = 0
        program_filename = sys.argv[1]

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8 -> store 8 in R0
        #     0b00000000,  # represent R0
        #     0b00001000,  # represent the value 8
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        with open(program_filename) as f:
            for line in f:
                line = line.split("#")
                line = line[0].strip()

                if line == "":
                    continue

                self.ram[address] = int(line, 2)
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == 0b10100000:  # ADD
            self.reg[reg_a] += self.reg[reg_b]
        elif op == 0b10100010:  # MUL
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 0b10100001:  # SUB
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == 0b10100011:  # DIV
            self.reg[reg_a] /= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
                        Handy function to print out the CPU state. You might want to call this
                        from run() if you need help debugging.
                        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def ram_read(self, MAR):
        """Should accept the address to read and return the value stored there"""
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        """Should accept a value to write, and the address to write it to."""
        self.ram[MAR] = MDR

    def handle_print(self, op_a=None, op_b=None):
        ''' Print value from register '''
        register_num = op_a
        value = self.reg[register_num]
        print(value)
        self.pc += 2

    def handle_halt(self, op_a=None, op_b=None):
        ''' Stops program from running '''
        self.running = False

    def handle_ldi(self, op_a=None, op_b=None):
        ''' Store values in the register '''
        register_num = op_a
        value = op_b

        self.reg[register_num] = value
        self.pc += 3

    def handle_push(self, op_a=None, op_b=None):
        # decrement the stack pointer
        self.reg[self.SP] -= 1   # address_of_the_top_of_stack -= 1

        # copy value from register into memory
        # reg_num = self.ram[self.pc + 1]
        reg_num = op_a

        value = self.reg[reg_num]  # this is what we want to push

        address = self.reg[self.SP]
        self.ram[address] = value   # store the value on the stack

        self.pc += 2

    def handle_pop(self, op_a=None, op_b=None):
        # copy value from memory into register
        address = self.reg[self.SP]
        value = self.ram[address]

        # reg_num = self.ram[self.pc + 1]
        reg_num = op_a

        self.reg[reg_num] = value

        # increment the stack pointer
        self.reg[self.SP] += 1

        self.pc += 2

    def run(self):
        """Run the CPU."""
        # PC = self.pc

        while self.running:
            # read the memory address that's stored in register PC and store that result in IR, Instruction Register
            IR = self.ram[self.pc]
            register_a = self.ram_read(self.pc + 1)
            register_b = self.ram_read(self.pc + 2)
            use_alu = (IR & 0b110000) >> 5

            if use_alu:
                self.alu(IR, register_a, register_b)
                self.pc += 3
            elif self.branchtable.get(IR):
                self.branchtable[IR](register_a, register_b)
            else:
                print("Unknown instruction")
                self.running = False

            self.trace()
            # if IR == self.LDI:
            #     register_num = self.ram_read(PC + 1)
            #     value = self.ram_read(PC + 2)
            #     self.reg[register_num] = value
            #     PC += 3
            # elif IR == self.PRN:
            #     register_num = self.ram_read(PC + 1)
            #     value = self.reg[register_num]
            #     print(value)
            #     PC += 2
            # elif IR == self.MUL:
            #     register_a = self.ram_read(PC + 1)
            #     register_b = self.ram_read(PC + 2)
            #     value = self.reg[register_a] * self.reg[register_b]
            #     self.reg[register_a] = value
            #     PC += 3
            # elif IR == self.HLT:
            #     self.running = False
            # else:
            #     print("Uknown instruction")
            #     self.running = False
