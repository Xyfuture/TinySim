

from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.stall import StallEvent


class Transfer(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Transfer, self).__init__()

        self.reg_file = reg_file
        self.current_eu = None

        self.first_response = False # 第一次收到指令
        self.busy_cycles = 0 # 这个为0表示数据传输指令结束
        self.stalled = False # 该部件向外发出了stall，到时间需要取消



    def ticktock(self):

        # 处理向外发送数据
        self.compute_cycle_energy()
        self.add_cycle_cnt()


    def update(self):
        pass

    # 有问题，数据传输的cycle是不确定的、
    def stall_out(self):
        pass


    def compute_cycle_energy(self):
        pass


