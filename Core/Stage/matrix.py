from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.reg import Register
from Core.Utils.stall import StallEvent


class Matrix(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Matrix, self).__init__()

        self.reg_file = reg_file

        self.current_eu = None

        self.inner_reg = Register()
        # self.inner_reg.stalled = False # 这个的时序有点难写
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'


        self.stall_reg = Register()
        self.stall_reg.stalled = False
        self.stall_event = None


    def ticktock(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.inner_reg.state == 'idle':
            if self.current_eu == 'veu':
                cycles = self.set_busy_cycle()
                self.inner_reg.busy_cycle = cycles

                if cycles > 0:
                    self.inner_reg.state = 'busy'

        if self.inner_reg.state == 'busy':
            if self.inner_reg.busy_cycle -1 == 0:
                self.inner_reg.state = 'idle'
            self.inner_reg.busy_cycle = self.inner_reg.busy_cycle - 1


        self.inner_reg.update()


    def update(self):
        if self.check_not_stalled():
            if self.inner_reg.state == 'idle':
                self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']

    def stall_out(self):

        self.stall_event = None
        if self.stall_reg.stalled:
            if self.inner_reg.state == 'idle':
                self.stall_event = StallEvent('MatrixExecuteUnit',False)
                self.stall_reg.stalled = False
        else:
            if self.inner_reg.state == 'busy':
                bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
                eu, inst = bypass_info['eu'], bypass_info['inst']
                if eu == 'meu':
                    self.stall_reg.stalled = True
                    self.stall_event = StallEvent('MatrixExecuteUnit', True)

        self.stall_reg.update()
        return self.stall_event

    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        return  1