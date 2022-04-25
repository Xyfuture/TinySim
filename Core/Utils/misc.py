from Core.Instruction.inst import instruction


class ExecInfo:
    def __init__(self,eu,inst:instruction,rd_value=0,rs1_value=0,rs2_value=0,length=0,start_addr=None):
        self.eu = eu
        self.inst = inst
        self.rd_value = rd_value
        self.rs1_value = rs1_value
        self.rs2_value = rs2_value
        self.length = length
        self.write_start_addr = start_addr


    def __getitem__(self, item):
        return self.__getattribute__(item)
