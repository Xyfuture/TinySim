from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.stall import StallEvent
from Core.Utils.reg import Register

class Vector(StageBase):
    def __init__(self):
        super(Vector, self).__init__()

        self.info  = None

        self.vvset_length = 0
        self.vvset_bitwidth = 0

        self.current_eu = None

        # 这几个是内部的寄存器，时钟下沿进行更新
        self.stalled = False # stall_out 控制
        self.busy_cycles = 0 # 需要额外等的周期数，本身已经占了一个周期了，除了本周期还需要多少个周期
        self.state = 'idle'  # 表示下一个周期的情况，给update,stall_out使用的

        self.inner_reg = Register()
        # self.inner_reg.stalled = False
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'


        self.stall_reg = Register()
        self.stall_reg.stalled = False
        self.stall_event = None

    def ticktock(self):

        self.add_cycle_cnt()
        self.compute_cycle_energy()


        # 使用register之后
        if self.inner_reg.state == 'idle':
            if self.current_eu == 'veu':
                if self.stage_data.op == 'vvset':
                    self.vvset()

                cycles = self.set_busy_cycle()
                self.inner_reg.busy_cycles = cycles
                if cycles > 0:
                    self.inner_reg.state = 'busy'

        if self.inner_reg.state == 'busy':
            if self.inner_reg.busy_cycles-1 == 0:
                self.inner_reg.state = 'idle'
            self.inner_reg.busy_cycles = self.inner_reg.busy_cycles -1


        # 时钟下降沿
        self.inner_reg.update() # 更新reg信息


    def update(self):
        if self.check_not_stalled():
            # idle 模式，说明该部件当前没有在处理指令
            if self.inner_reg.state == 'idle':
                self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
                self.info = self.recv_data
        # 其他模式都不会更新stage_data



    def stall_out(self):

        self.stall_event = None
        if self.stall_reg.stalled:
            if self.inner_reg.state == 'idle':
                self.stall_event = StallEvent('VectorExecuteUnit',False)
                self.stall_reg.stalled = False
        else:
            if self.inner_reg.state == 'busy':
                bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
                eu,inst = bypass_info['eu'],bypass_info['inst']
                if eu == 'veu':
                    self.stall_reg.stalled = True
                    self.stall_event = StallEvent('VectorExecuteUnit',True)


        return self.stall_event


    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        return 1


    def vvset(self):
        if self.stage_data.op == 'vvset':
            self.vvset_length = self.info.rd_value
            self.vvset_bitwidth = self.stage_data.bitwidth


    def bypass_ticktock(self):
        if self.inner_reg.state == 'busy':
            if self.inner_reg.busy_cycle -1 == 0:
                return (self.info.rd_value,self.info.rd_value+self.info.length-1) # length 是设置过的
        return None