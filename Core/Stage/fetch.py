

from Core.Stage.base import StageBase
from Core.Utils.inst import InstBuffer


class Fetch(StageBase):
    def __init__(self):
        super(Fetch, self).__init__()

        self.pc = 0
        self.inst_buffer = InstBuffer()

    def recv(self,pre_stage_data):
        pass

    def send(self):
        return self.inst_buffer[self.pc-1] # pc是个寄存器，在ticktock中的+1 应该发生在这之后

    def ticktock(self):
        self.add_cycle_cnt()
        if self.check_stalled():
            pass
        else:
            self.pc += 1

        self.compute_cycle_enery()


    def stall_out(self):
        return None

    def compute_cycle_enery(self):
        pass


    def update(self):
        pass



