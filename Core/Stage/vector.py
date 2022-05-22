from Core.Instruction.inst import instruction
from Core.Stage.Storage.mem import ScratchPad
from Core.Stage.base import StageBase
from Core.Utils.misc import ExecInfo
from Core.Stage.stall import StallEvent
from Core.Utils.reg import Register

class Vector(StageBase):
    def __init__(self,scratchpad):
        super(Vector, self).__init__()
        self.level = 5

        self.scratchpad = scratchpad

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'


        self.vvset_reg = Register('neg')
        self.vvset_reg.vvset_length = 0
        self.vvset_reg.vvset_bitwidth = 0


        # 内部的寄存器，在时钟的下降沿更新内容
        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0

        # self.stage_reg.finish = 0 # 使用这个要保证busy_cycle必须时间大于1，至少执行两个周期

        self.alu_length = 32 # 32 * 1 Byte
        # self.alu_per_energy = 0

        self.dynamic_per_energy = 1.75875625 * self.alu_length
        self.leakage_per_energy = 0.1396375 * self.alu_length


    # 目前没有考虑stall的情况
    def set_pos_reg(self):
        if self.state == 'idle':
            tmp = self.pre_stage_list[0].send_data
            self.stage_reg.info = tmp
            self.stage_reg.current_eu,self.stage_reg.stage_data = tmp['eu'],tmp['inst']

        # if self.inner_reg.busy_cycle == 1:
        #     self.stage_reg.finish = 1
        # else:
        #     self.stage_reg.finish = 0

    def pos_tick(self):
        self.add_cycle_cnt()


    def set_neg_reg(self):
        if self.state == 'busy':
            self.inner_reg.busy_cycle = self.inner_reg.busy_cycle-1
        elif self.state == 'idle':
            self.vvset()
            if self.stage_reg.current_eu == 'veu':
                self.inner_reg.busy_cycle = self.set_busy_cycle()

    @property
    def send_data(self):
        return 0

    @property
    def state(self):
        if self.inner_reg.busy_cycle > 0:
            return 'busy'
        else:
            return 'idle'

    @property
    def finish_interval(self):
        interval = None

        # mem Queue 在上升沿更新，因此使用state即可知道指令是否执行结束

        if self.stage_reg.current_eu == 'veu' and self.state == 'idle':
            start_addr = self.stage_reg.info.write_start_addr
            length = self.stage_reg.info.length

            if start_addr:
                interval = (start_addr,start_addr+length-1)

        return interval


    def stall_info(self):
        if self.state == 'busy':
            info = self.pre_stage_list[0].send_data
            if info['eu'] == 'veu':
                return StallEvent("VectorExecuteUnit",self.level)
        return None


    def compute_dynamic_energy(self):
        self.dynamic_energy += self.dynamic_per_energy

    def compute_leakage_energy(self):
        self.leakage_energy = self.leakage_per_energy * self.total_cycles

    def set_busy_cycle(self):
        self.compute_dynamic_energy()

        if self.stage_reg.stage_data.op == 'vvset':
            return 0
        elif self.stage_reg.stage_data.op[0] == 'v':
            data_size = self.vvset_reg.vvset_length * self.vvset_reg.vvset_bitwidth
            read_latency = self.scratchpad.read_mem(data_size) * 2
            write_latency = self.scratchpad.read_mem(data_size)
            compute_latency = data_size/self.alu_length
            if self.stage_reg.stage_data.op[0] == 'vvmul':
                compute_latency *= 4
            return read_latency+write_latency+compute_latency



        return 0

    def vvset(self):
        if self.stage_reg.stage_data.op == 'vvset':
            self.vvset_reg.vvset_length = self.stage_reg.info.rd_value
            self.vvset_reg.vvset_bitwidth = self.stage_reg.stage_data.bitwidth


    def dump_info(self):
        return ('Vector:\n'
              'inst:{}\n'
              'stall:{}\n'
              'busy_cycle:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level),self.inner_reg.busy_cycle))