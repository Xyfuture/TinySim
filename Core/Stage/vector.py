from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.stall import StallEvent


class Vector(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Vector, self).__init__()

        self.reg_file = reg_file
        self.vvset_length = 0
        self.vvset_bitwidth = 0

        self.current_eu = None
        self.first_response = False
        self.stalled = False
        self.busy_cycles = 0

        self.state = 'idle'
        self.receivable = True # 可以接收新信息，这个主要是为了解决一个很别扭的问题


    def ticktock(self):

        if self.busy_cycles <= 1:
            self.receivable = True
        else:
            self.receivable = False

        self.add_cycle_cnt()
        self.compute_cycle_energy()

        self.first_response = False


    def update(self):
        eu,inst = self.recv_data['eu'],self.recv_data['inst']

        # 正在处理中,更改busy_cycle等信息
        if self.busy_cycles > 0:
            self.busy_cycles -= 1
            if self.busy_cycles == 0:
                self.state = 'idle'


        # 没在处理，正好是该部件的指令
        if self.receivable and eu == 'veu':
            self.first_response = True
            self.state = 'busy'

            self.stage_data = inst
            self.set_busy_cycle()




    def stall_out(self):

        # 最后一个周期，同时暂停了其他的部件
        if self.busy_cycles == 1 and self.stalled:
            self.stalled = False
            return StallEvent('VectorExecuteUnit',False)

        # 正在处理中(不马山结束),且没有暂停其他的部件
        if self.busy_cycles>1 and not self.stalled:
            issue_info = self.bypass_pre_stage_list[0].bypass_ticktock()
            eu,inst = issue_info['eu'],issue_info['inst']

            if eu == 'veu':
                self.stalled = True
                return StallEvent('VectorExecuteUnit',True)

        return None


    def compute_cycle_energy(self):
        pass


    def set_busy_cycle(self):
        pass


