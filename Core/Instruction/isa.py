from Core.Instruction.inst import instruction

OPCODE_MAP_B2S ={
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

VVARITH_MAP_B2S={
 '00001': 'vvadd',
 '00010': 'vvsub',
 '00011': 'vvmul',
 '10001': 'vvgtm',
 '10010': 'vvgt',
 '10011': 'vveq',
 '10100': 'vvand',
 '10101': 'vvor'
}

VVSHIFT_MAP_B2S = {
    "00001":'vvsll',
    '00010':'vvsrl'
}

VACT_MAP_B2S = {
    '00001':'vrelu',
    '00010':'vsigmoid',
    '00011':'vtanh'
}

SREG_MAP_B2S = {
    '00001': 'sadd',
    '00010': 'ssub',
    '00011': 'smul',
    '00100': 'sidv'
}

RE_MAP = {
    'vvarith':VVARITH_MAP_B2S,
    'vvshift':VVSHIFT_MAP_B2S,
    'vact':VACT_MAP_B2S,
    'sreg':SREG_MAP_B2S
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


FUNCT5_MAP = {
    'vvadd':'00001',
    'vvsub':'00010',
    'vvmul':'00011',
    'vvgtm':'10001',
    'vvgt':'10010',
    'vveq':'10011',
    'vvand':'10100',
    'vvor':'10101',

    'vvsll':'00001',
    'vvsra':'00010',

    'vrelu':'00001',
    'vsigmoid':'00010',
    'vtanh':'00011',

    'sadd':'00001',
    'ssub':'00010',
    'smul':'00011',
    'sidv':'00100'
}

OPCODE_MAP ={
    "vvset":'0010001',
    "vvadd":'0010010',
    "vvsub":'0010010',
    "vvmul":'0010010',
    "vvgtm":'0010010',
    "vvgt":'0010010',
    "vveq":'0010010',
    "vvand":'0010010',
    "vvor":'0010010',
    "vvsll":'0010011',
    "vvsra":'0010011',
    "vvdmul":'0010100',
    "vinvt":'0010101',
    "vrandg":'0010111',
    "vrelu":'0011000',
    "vsigmoid":'0011000',
    "vtanh":'0011000',
    "vmv":'0011001',
    "sadd":'0100001',
    "ssub":'0100001',
    "smul":'0100001',
    "sdiv":'0100001',
    "saddi":'0100010',
    "ssubi":'0100011',
    "smuli":'0100100',
    "send":'0110001',
    "recv":'0110010',
    "ld":'0110011',
    "st":'0110100',
    "sti":'0110101',
    "ldi":'0110110',
    "bind":'1000001',
    "unbind":'1000010',
    "gemv":'1000011',
    "gvr":'1000100'
}


FUNCT_LIST_MAP = {
    "vvset":['rd_dump','bitwidth_dump'],
    "vvadd":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvsub":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvmul":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvgtm":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvgt":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vveq":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvand":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvor":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "vvsll":['rd_dump','rs1_dump','rs2_dump','funct5_dump','bitwidth_dump'],
    "vvsra":['rd_dump','rs1_dump','rs2_dump','funct5_dump','bitwidth_dump'],
    "vvdmul":['rd_dump','rs1_dump','rs2_dump'],
    "vinvt":['rd_dump','rs1_dump'],
    "vrandg":['rd_dump'],
    "vrelu":['rd_dump','rs1_dump','funct5_dump'],
    "vsigmoid":['rd_dump','rs1_dump','funct5_dump'],
    "vtanh":['rd_dump','rs1_dump','funct5_dump'],
    "vmv":['rd_dump','rs1_dump','rs2_dump','imm_v_dump'],
    "sadd":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "ssub":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "smul":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "sdiv":['rd_dump','rs1_dump','rs2_dump','funct5_dump'],
    "saddi":['rd_dump','rs1_dump','imm_s_dump'],
    "ssubi":['rd_dump','rs1_dump','imm_s_dump'],
    "smuli":['rd_dump','rs1_dump','imm_s_dump'],
    "send":['rs2_dump','rs1_dump','imm_d_dump'],
    "recv":['rs2_dump','rs1_dump','imm_d_dump'],
    "ld":['rd_dump','rs1_dump'],
    "st":['rd_dump','rs1_dump','rs2_dump'],
    "sti":['rd_dump','rs1_dump'],
    "ldi":['rd_dump','imm_l_dump'],
    "bind":['rd_dump','rs1_dump','rs2_dump','imm_m_dump','bitwidth_dump'],
    "unbind":['rd_dump'],
    "gemv":['rd_dump','rs1_dump','rs2_dump','bitwidth_dump'],
    "gvr":['rd_dump','rs1_dump','rs2_dump']
    }


class BinaryDump:
    def __init__(self,inst:instruction):
        self.inst = inst
        self.binary = BinaryInst()

    def dump(self):
        return self.get_binary().dump()

    def get_binary(self):
        func_list = FUNCT_LIST_MAP[self.inst.op]
        self.opcode_dump()
        for f in func_list:
            tmp_func = self.__getattribute__(f)
            tmp_func()
        return self.binary

    def opcode_dump(self):
        self.binary[0:7] = OPCODE_MAP[self.inst.op]

    def rd_dump(self):
        assert 0<= self.inst.rd <= 31
        self.binary[7:12] = '{:05b}'.format(self.inst.rd)

    def rs1_dump(self):
        assert 0 <= self.inst.rs1 <= 31
        self.binary[12:17] = '{:05b}'.format(self.inst.rs1)

    def rs2_dump(self):
        assert 0 <= self.inst.rs2 <= 31
        self.binary[17:22] = '{:05b}'.format(self.inst.rs2)

    def funct5_dump(self):
        self.binary[22:27] = FUNCT5_MAP[self.inst.op]

    def bitwidth_dump(self):
        # 暂时是表示的几个byte，也可以转换为2^x的表示方式
        self.binary[29:32] = '{:03b}'.format(self.inst.bitwidth)


    # 现在所有的立即数都是没有check过的，因此可能会出现溢出的问题，需要注意
    def imm_v_dump(self):
        self.binary[22:32] = '{:010b}'.format(self.inst.imm)

    def imm_s_dump(self):
        self.binary[17:32] = '{:015b}'.format(self.inst.imm)

    def imm_d_dump(self):
        self.binary[22:32] = '{:010b}'.format(self.inst.imm)

    def imm_l_dump(self):
        self.binary[12:32] = '{:020b}'.format(self.inst.imm)

    def imm_m_dump(self):
        self.binary[22:29] = '{:07b}'.format(self.inst.imm)