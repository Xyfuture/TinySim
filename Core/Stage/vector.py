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

        # 这几个是内部的寄存器，时钟下沿进行更新
        self.stalled = False # stall_out 控制
        self.busy_cycles = 0 # 需要额外等的周期数，本身已经占了一个周期了，除了本周期还需要多少个周期
        self.state = 'idle'  # 表示下一个周期的情况，给update,stall_out使用的



    def ticktock(self):

        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.state == 'idle':
            if self.current_eu == 'veu':
                self.set_busy_cycle()
                if self.busy_cycles > 0: # 如果为0，则不需要设置了
                    self.state = 'busy'
                return

        if self.state == 'busy':
            if self.busy_cycles - 1 > 0:
                self.state = 'busy'
            else:
                self.state = 'idle'
            self.busy_cycles -= 1
            return

    def update(self):
        if self.check_not_stalled():
            # idle 模式，说明该部件当前没有在处理指令
            if self.state == 'idle':
                self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
        # 其他模式都不会更新stage_data

    def stall_out(self):
        # 这里有个不太好的地方，其实不应该把stalled这个寄存器更新放在这里，应该放在ticktock中，因为他们在一起更新

        # 目前没有stall其他部件，检测是否需要stall其他部件
        if not self.stalled:
            # 下个周期是否忙，如果忙那么要对bypass过来的数据处理，确保下一周期不会发生数据的传递
            if self.state == 'busy':
                bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
                eu,inst = bypass_info['eu'],bypass_info['inst']
                if eu == 'veu':
                    self.stalled = True
                    return StallEvent("VectorExecuteUnit",True)

        # 目前已经阻塞了其他的部件
        if self.stalled:
            # 下个周期不忙，取消stall
            if self.state == 'idle':
                self.stalled = False
                return StallEvent('VectorExecuteUnit',False)




    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        pass


