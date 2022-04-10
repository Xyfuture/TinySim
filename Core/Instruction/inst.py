

from Core.Instruction.isa import OPCODE_MAP_B2S, RE_MAP, BinaryInst,BinaryDump

class instruction:

    RD_RS1_RS2 = ['vvadd','vvsub','vvmul','vvgtm','vvgt','vveq','vvand','vvor','vvsll''vvsra','vvdmul','vmv',
                  'sadd','ssub','smul','sdiv',
                  'st','bind','gemv','gvr']

    RD_RS1 = ['vinvt','vrelu','vsigmoid','vtanh',
              'saddi','ssubi','smuli',
              'ld','sti']

    RD = ['vvset','vrandg','unbind','ldi']

    RS1_RS2 = ['send','recv']

    IMM = ['vmv','saddi','ssubi','smuli','send','recv','sti','bind','ldi'] # unchecked

    BITWIDTH = ['vvset','vvsll','vvsra','bind','gemv']

    def __init__(self,op=''):
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.bitwidth = 0
        self.op = op

        self.binary_inst = BinaryInst()

    def read_dict(self,inst_dict:dict):
        for k,v in inst_dict.items():
            self.__setattr__(k,v)
        self.binary_inst = BinaryDump(self).get_binary()


    def read_binary(self,binary_inst):
        self.binary_inst = binary_inst
        self.binary_parse()

    def dump_binary(self):
        return self.binary_inst.dump()

    def dump_asm(self):
        _str = self.op

        reg_str = ''
        if self.op in self.RD_RS1_RS2:
            reg_str = ' rd:'+str(self.rd)+' rs1:'+str(self.rs1)+' rs2:'+str(self.rs2)
        elif self.op in self.RD_RS1:
            reg_str = ' rd:' + str(self.rd) + ' rs1:' + str(self.rs1)
        elif self.op in self.RD:
            reg_str = ' rd:' + str(self.rd)
        elif self.op in self.RS1_RS2:
            reg_str = ' rs1:' + str(self.rs1) + ' rs2:'+str(self.rs2)

        imm_str = ''
        if self.op in self.IMM:
            imm_str = ' imm:'+str(self.imm)

        bitwidth_str = ''
        if self.op in self.BITWIDTH:
            bitwidth_str = ' bitwidth:'+str(self.bitwidth)

        _str += reg_str+imm_str+bitwidth_str
        return _str

    # binary 解析部分
    def opcode_binary_parse(self):
        funct5_op = ['vvarith','vvshift','vact','sreg']

        tmp_op = OPCODE_MAP_B2S[self.binary_inst[0:7]]
        if tmp_op in funct5_op:
            self.op = RE_MAP[tmp_op][self.binary_inst[22:27]]
        else:
            self.op = tmp_op

    def reg_binary_parse(self):
        self.rd = int(self.binary_inst[7:12],2)
        self.rs1 = int(self.binary_inst[12:17],2)
        self.rs2 = int(self.binary_inst[17:22],2)

    def imm_binary_parse(self):
        # 仅仅支持 core_id imm 应该就这个还有点用吧
        self.imm = int(self.binary_inst[22:32],2)

    def bitwidth_binary_parse(self):
        self.bitwidth = int(self.binary_inst[29:32],2)

    def binary_parse(self):
        self.opcode_binary_parse()
        self.reg_binary_parse()
        self.imm_binary_parse()
        self.bitwidth_binary_parse()




class InstBuffer:
    def __init__(self):
        self.size = 0
        self.inst_list = []

    def load_binary(self,file_name):
        with open(file_name,'r') as f:
            for line in f.readlines():
                line = line.strip()

    def load_dict(self,file_name):
        pass


    def print_asm(self):
        for inst in self.inst_list:
            print(inst.dump_asm())

    def print_binary(self):
        for inst in self.inst_list:
            print(inst.dump_binary())

    def dump_asm(self):
        for inst in self.inst_list:
            yield inst.dump_asm()

    def dump_binary(self):
        for inst in self.inst_list:
            yield inst.dump_binary()

    def __getitem__(self, item):
        return self.inst_list[item]

    def __setitem__(self, key, value):
        assert isinstance(value,instruction)
        self.inst_list[key] = value