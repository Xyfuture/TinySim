from Core.Utils.inst import instruction

OPCODE_MAP ={
 '0010001': 'vvset',
 '0010010': 'vvarith',
 '0010011': 'vvshift',
 '0010100': 'vvdmul',
 '0010101': 'vinvt',
 '0010111': 'vrandg',
 '0011000': 'vact',
 '0011001': 'vmv',
 '0100001': 'sreg',
 '0100010': 'saddi',
 '0100011': 'ssubi',
 '0100100': 'smuli',
 '0110001': 'send',
 '0110010': 'recv',
 '0110011': 'ld',
 '0110100': 'st',
 '0110101': 'sti',
 '0110110': 'ldi',
 '1000001': 'bind',
 '1000010': 'unbind',
 '1000011': 'gemv',
 '1000100': 'gvr'
}

VVARITH_MAP={
 '00001': 'vvadd',
 '00010': 'vvsub',
 '00011': 'vvmul',
 '10001': 'vvgtm',
 '10010': 'vvgt',
 '10011': 'vveq',
 '10100': 'vvand',
 '10101': 'vvor'
}

VVSHIFT_MAP = {
    "00001":'vvsll',
    '00010':'vvsrl'
}

VACT_MAP = {
    '00001':'vrelu',
    '00010':'vsigmoid',
    '00011':'vtanh'
}

SREG_MAP = {
    '00001': 'sadd',
    '00010': 'ssub',
    '00011': 'smul',
    '00100': 'sidv'
}

RE_MAP = {
    'vvarith':VVARITH_MAP,
    'vvshift':VVSHIFT_MAP,
    'vact':VACT_MAP,
    'sreg':SREG_MAP
}




# copy from TinyCompiler
class BinaryInst:
    # 注意一个问题，高低位反转的问题，我们正常看一个数组是从0到31，首先出现的数是低位，但对于verilog而言是31到0，首先出现的数是高位
    def __init__(self):
        self.inst_array =['0' for _ in range(32)]

    def __setitem__(self, key, value):
        if isinstance(key,int):
            assert isinstance(value,str) and value in ['1','0']
            self.inst_array[key] = value
        elif isinstance(key,slice):
            start = key.start
            stop = key.stop

            assert start >=0 and stop<=32
            assert stop - start == len(value)

            # 注意这里是反转的
            for i,k in enumerate(reversed(value)):
                assert k in ['0','1']
                self.inst_array[start+i] = k

    def __getitem__(self, item):
        if isinstance(item,int):
            return self.inst_array[item]
        elif isinstance(item,slice):
            _str = ''
            # 反转一下 有点别扭，slice给的是小到大，但反的数据是大位到小位
            for i in reversed(self.inst_array[item]):
                _str += i
            return _str

    def dump(self):
        _str = ''
        # 反转一下，第一个数是最高位
        for i in reversed(self.inst_array):
            _str += i
        return _str


class BinaryParse:
    def __init__(self,binary_inst:BinaryInst):
        default_value = {'rd': 0, 'rs1': 0, 'rs2': 0, 'bitwidth': 0, 'imm': 0}
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.imm = 0
        self.bitwidth = 0
        self.op = ''

        self.binary_inst = binary_inst

    def opcode_parse(self):
        funct5_op = ['vvarith','vvshift','vact','sreg']

        tmp_op = OPCODE_MAP[self.binary_inst[0:7]]
        if tmp_op in funct5_op:
            self.op = RE_MAP[tmp_op][self.binary_inst[22:27]]
        else:
            self.op = tmp_op

    def reg_parse(self):
        self.rd = int(self.binary_inst[7:12],2)
        self.rs1 = int(self.binary_inst[12:17],2)
        self.rs2 = int(self.binary_inst[17:22],2)

    def imm_parse(self):
        # 仅仅支持 core_id imm 应该就这个还有点用吧
        self.imm = int(self.binary_inst[22:32],2)

    def bitwidth_parse(self):
        self.bitwidth = int(self.binary_inst[29:32],2)

    def parse(self):
        self.opcode_parse()
        self.reg_parse()
        self.imm_parse()
        self.bitwidth_parse()

        tmp_inst = instruction(self.op)

        tmp_inst.rd = self.rd
        tmp_inst.rs1 = self.rs1
        tmp_inst.rs2 = self.rs2
        tmp_inst.imm = self.imm
        tmp_inst.bitwidth = self.bitwidth
