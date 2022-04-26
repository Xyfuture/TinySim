from Core.Instruction.inst import instruction
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.misc import ExecInfo
from Core.Stage.stall import StallEvent
from Core.Utils.reg import Register

class Vector(StageBase):
    def __init__(self):
        super(Vector, self).__init__()
        self.level = 5

        self.stage_reg.info = ExecInfo(eu='none', inst=instruction())
        self.stage_reg.current_eu = 'none'


        self.vvset_reg = Register('neg')
        self.vvset_reg.vvset_length = 0
        self.vvset_reg.vvset_bitwidth = 0


        # 内部的寄存器，在时钟的下降沿更新内容
        self.inner_reg = Register('neg')
        self.inner_reg.busy_cycle = 0

        # self.stage_reg.finish = 0 # 使用这个要保证busy_cycle必须时间大于1，至少执行两个周期

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
        self.compute_cycle_energy()


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


    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        if self.stage_reg.stage_data.op == 'none':
            return 0
        if self.stage_reg.stage_data.op == 'vvset':
            return 0
        return 2

    def vvset(self):
        if self.stage_reg.stage_data.op == 'vvset':
            self.vvset_reg.vvset_length = self.stage_reg.info.rd_value
            self.vvset_reg.vvset_bitwidth = self.stage_reg.stage_data.bitwidth


    def dump_info(self):
        return ('Vector:\n'
              'inst:{}\n'
              'stall:{}\n'
              'busy_cycle:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level),self.inner_reg.busy_cycle))