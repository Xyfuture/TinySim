import copy

from Core.Instruction.inst import instruction
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.reg import Register
from Core.Utils.misc import ExecInfo
from Core.Stage.stall import StallEvent


# 针对内存而言的，READ指对应寄存器的值是要读取的内存的地址
RS1_READ = {"vvadd","vvsub","vvmul","vvgtm","vvgt","vveq","vvand","vvor","vvsll","vvsra","vvdmul","vinvt","vrelu","vsigmoid","vtanh","vmv",
            "send","ld",
            "gemv"} # 将rs1所存的数值作为地址的指令
RS2_READ = {"vvadd","vvsub","vvmul","vvgtm","vvgt","vveq","vvand","vvor","vvsll","vvsra","vvdmul","vmv"}
RD_READ = {}

RS1_WRITE = {"recv","gvr"}
RS2_WRITE = {}
RD_WRITE = {"vvadd","vvsub","vvmul","vvgtm","vvgt","vveq","vvand","vvor","vvsll","vvsra","vvdmul","vinvt","vrandg","vrelu","vsigmoid","vtanh","vmv",
            "st"} # sti remove



class MemQueue(StageBase):
    def __init__(self,reg_file:RegFile):
        super(MemQueue, self).__init__()
        self.level = 4

        # stage_data 仍旧是inst类型的
        self.stage_reg.current_eu = 'none'

        self.reg_file = reg_file

        self.vvset_reg = Register('neg')
        self.vvset_reg.vvset_length = 0
        self.vvset_reg.vvset_bitwidth = 0


        self.queue_reg = Register()
        self.queue_reg.write_queue = []

        self.pre_reg = Register('neg')
        self.pre_reg.pre_interval = None

    def set_pos_reg(self):
        if self.state == 'idle':
            if self.stall_engine.check_not_stall(self.level):
                tmp = self.pre_stage_list[0].send_data
                self.stage_reg.current_eu,self.stage_reg.stage_data = tmp['eu'],tmp['inst']

            queue = copy.deepcopy(self.queue_reg.write_queue)
            for stage in self.bypass_pre_stage_list:
                finish_interval = stage.finish_interval
                if finish_interval:
                    queue.remove(finish_interval)
            if self.stall_engine.check_not_stall(self.level):
                if self.pre_reg.pre_interval:
                    queue.append(self.pre_reg.pre_interval)
            self.queue_reg.write_queue = queue

        elif self.state == 'busy':
            queue = copy.deepcopy(self.queue_reg.write_queue)
            for stage in self.bypass_pre_stage_list:
                finish_interval = stage.finish_interval
                if finish_interval:
                    queue.remove(finish_interval)
            # 不需要添加上一条指令的
            self.queue_reg.write_queue = queue

    def pos_tick(self):
        self.add_cycle_cnt()
        self.compute_dynamic_energy()




    def set_neg_reg(self):
        self.vvset()

        # if self.stall_engine.check_not_stall(self.level):
        #     if self.state == 'idle':
        #         length = self.gen_mem_length()
        #         start_addr = self.gen_mem_write_start_addr()
        #
        #         if start_addr:
        #             interval = (start_addr,start_addr+length-1)
        #             self.pre_reg.pre_interval = interval
        #         else:
        #             self.pre_reg.pre_interval = None
        #     else:
        #         self.pre_reg.pre_interval = None
        # else:
        #     self.pre_reg.pre_interval = None
        length = self.gen_mem_length()
        start_addr = self.gen_mem_write_start_addr()

        if start_addr:
            interval = (start_addr, start_addr + length - 1)
            self.pre_reg.pre_interval = interval
        else:
            self.pre_reg.pre_interval = None

    @property
    def send_data(self):
        if self.state == 'busy':
            tmp = ExecInfo('none',instruction())
            return tmp
        elif self.state == 'idle':
            inst = self.stage_reg.stage_data
            rd_value = self.reg_file[inst.rd ]
            rs1_value = self.reg_file[inst.rs1]
            rs2_value = self.reg_file[inst.rs2]

            length = self.gen_mem_length()
            start_addr = self.gen_mem_write_start_addr()
            tmp = ExecInfo(self.stage_reg.current_eu, inst, rd_value, rs1_value, rs2_value,length,start_addr)
            return tmp
        return None

    def stall_info(self):
        if self.state == 'busy':
            info = self.pre_stage_list[0].send_data
            if info['eu'] in ['veu','meu','dtu']:
                return StallEvent("MemoryQueue",self.level)
        return None

    def compute_dynamic_energy(self):
        pass

    def compute_leakage_energy(self):
        pass

    def vvset(self):
        if self.stage_reg.stage_data.op == 'vvset':
            self.vvset_reg.vvset_bitwidth = self.stage_reg.stage_data.bitwidth
            self.vvset_reg.vvset_length =self.reg_file[self.stage_reg.stage_data.rd]

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

    @property
    def state(self):
        length = self.gen_mem_length()
        inst = self.stage_reg.stage_data
        if inst.op in RD_READ:
            start_addr = self.reg_file[inst.rd]
            if self.is_overlap((start_addr,start_addr+length-1)):
                return 'busy'
        if inst.op in RS1_READ:
            start_addr = self.reg_file[inst.rs1]
            if self.is_overlap((start_addr,start_addr+length-1)):
                return 'busy'
        if inst.op in RS2_READ:
            start_addr = self.reg_file[inst.rs2]
            if self.is_overlap((start_addr,start_addr+length-1)):
                return 'busy'

        return 'idle'

    def gen_mem_length(self):
        inst = self.stage_reg.stage_data

        if inst.op[0] == 'v':
            bitwidth = self.vvset_reg.vvset_bitwidth
            if inst.op in ['vvsll','vvsrl']:
                bitwidth = inst.bitwidth
            return bitwidth*self.vvset_reg.vvset_length
        elif inst.op in ['send','recv','st']:
            return self.reg_file[inst.rs2]
        elif inst.op in ['gemv','gvr']:
            if inst.op == 'gemv':
                return inst.bitwidth * self.reg_file[inst.rs2]
            if inst.op == 'gvr':
                return self.reg_file[inst.rs2] * 4 # 4byte

        return 1

    def gen_mem_write_start_addr(self):
        inst = self.stage_reg.stage_data
        start_addr = None
        if inst.op in RS1_WRITE:
            start_addr = self.reg_file[inst.rs1]
        if inst.op in RS2_WRITE:
            start_addr = self.reg_file[inst.rs2]
        if inst.op in RD_WRITE:
            start_addr = self.reg_file[inst.rd]

        return start_addr

    def dump_info(self):
        return ('MemQueue:\n'
              'inst:{}\n'
              'stall:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level)))