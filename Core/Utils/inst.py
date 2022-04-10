

class instruction:
    def __init__(self,op=''):
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.bitwidth = 0
        self.op = op

    def read_binary(self):
        pass

    def read_asm(self):
        pass

    def dump_binary(self):
        pass

    def dump_asm(self):
        pass


class InstBuffer:
    def __init__(self):
        self.size = 0

    def load_asm(self):
        pass

    def load_binary(self):
        pass

    def print_asm(self):
        pass

    def print_binary(self):
        pass

    def dump_asm(self):
        pass

    def dump_binary(self):
        pass

    def __getitem__(self, item):
        pass

    def __setitem__(self, key, value):
        pass