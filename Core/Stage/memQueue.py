import copy

from Core.Instruction.inst import instruction
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.reg import Register
from Core.Utils.misc import ExecInfo
from Core.Utils.stall import StallEvent

RS1_READ = {} # 将rs1所存的数值作为地址的指令
RS2_READ = {}
RD_READ = {}

RS1_WRITE = {}
RS2_WRITE = {}
RD_WRITE = {}



class MemQueue(StageBase):
    def __init__(self,reg_file:RegFile):
        super(MemQueue, self).__init__()

        # stage_data 仍旧是inst类型的

        self.current_eu = 'none'

        self.reg_file = reg_file
        # self.write_queue = [] # 全部使用闭区间

        self.vvset_length = 0
        self.vvset_bitwidth = 0

        # self.inner_reg = Register()
        # self.inner_reg.state = 'idle'

        self.queue_reg = Register()
        self.queue_reg.write_queue = []


    def ticktock(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.stage_data.op == 'vvset':
            self.vvset()


        self.queue_reg.write_queue = self.write_queue_remove()

        self.queue_reg.update()

    def stall_out(self):
        self.queue_reg.write_queue = self.write_queue_add()

        if self.state == 'busy':
            self.send_data = ExecInfo('none',instruction())
        else:
            rd_value = self.reg_file[self.stage_data.rd_value ]
            rs1_value = self.reg_file[self.stage_data.rs1_value]
            rs2_value = self.reg_file[self.stage_data.rs2_value]

            length = self.gen_mem_length()
            tmp = ExecInfo(self.current_eu, self.stage_data, rd_value, rs1_value, rs2_value,length)
            self.send_data = tmp


        if self.state == 'busy':
            return StallEvent("MemoryQueue",True)
        else :
            return StallEvent("MemoryQueue",False) # 性能比较差


    def update(self):
        if self.check_not_stalled():
            if self.state == 'idle':
                self.current_eu, self.stage_data = self.recv_data['eu'], self.recv_data['inst']

        # 更新写入的信息
        self.queue_reg.update()


    def compute_cycle_energy(self):
        pass

    def bypass_ticktock(self):
        # 鉴于这里的bypass 都是后面的部件，所以前面的部件已经计算完了，所以直接传send_data
        return self.send_data

    def vvset(self):
        self.vvset_bitwidth = self.stage_data.bitwidth
        self.vvset_length =self.reg_file[self.stage_data.rd]

    def is_overlap(self,interval):
        # 闭区间下操作
        for cur in self.queue_reg.write_queue:
            if cur[0] <= interval[0] <= cur[1]:
                return True
            if cur[0] <= interval[1] <= cur[1]:
                return True
        return False

    def check_overlap(self,start_addr):
        length = self.gen_mem_length()
        return self.is_overlap((start_addr,start_addr+length-1))

    def write_queue_remove(self):
        queue = copy.deepcopy(self.queue_reg.write_queue)
        for stage in self.pre_stage_list:
            bypass_info = stage.bypass_ticktock()
            if bypass_info:
                queue.remove(bypass_info)
        return queue

    def write_queue_add(self):
        queue = copy.deepcopy(self.queue_reg.write_queue)

        length = self.gen_mem_length()
        if self.stage_data.op in RS1_WRITE:
            start_addr = self.reg_file[self.stage_data.rs1]
            queue.append((start_addr,start_addr+length-1))
        if self.stage_data.op in RS2_WRITE:
            start_addr = self.reg_file[self.stage_data.rs2]
            queue.append((start_addr,start_addr+length-1))
        if self.stage_data.op in RD_WRITE:
            start_addr = self.reg_file[self.stage_data.rd]
            queue.append((start_addr, start_addr + length - 1))

        return queue

    @property
    def state(self):
        if self.stage_data.op in RD_READ:
            start_addr = self.reg_file[self.stage_data.rd]
            if self.check_overlap(start_addr):
                return 'busy'
        if self.stage_data.op in RS1_READ:
            start_addr = self.reg_file[self.stage_data.rs1]
            if self.check_overlap(start_addr):
                return 'busy'
        if self.stage_data.op in RS2_READ:
            start_addr = self.reg_file[self.stage_data.rs2]
            if self.check_overlap(start_addr):
                return 'busy'

        return 'idle'


    def gen_mem_length(self):
        if self.stage_data.op[0] == 'v':
            bitwidth = self.vvset_bitwidth
            if self.stage_data.op in ['vvsll','vvsrl']:
                bitwidth = self.stage_data.bitwidth
            return bitwidth*self.vvset_length
        elif self.stage_data.op in ['send','recv','st']:
            return self.reg_file[self.stage_data.rs2]
        elif self.stage_data.op in ['gemv','gvr']:
            if self.stage_data.op == 'gemv':
                return self.stage_data.bitwidth * self.reg_file[self.stage_data.rs2]
            if self.stage_data.op == 'gvr':
                return self.reg_file[self.stage_data.rs2] * 4 # 4byte

        return 1
