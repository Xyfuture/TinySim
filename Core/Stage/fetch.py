

from Core.Stage.base import StageBase
from Core.Instruction.inst import InstBuffer


class Fetch(StageBase):
    def __init__(self):
        super(Fetch, self).__init__()

        self.pc = 0
        self.next_pc = 0
        self.inst_buffer = InstBuffer()


    def ticktock(self):
        self.send_data = self.inst_buffer[self.pc]

        if self.check_not_stalled():
            self.next_pc += 1


        self.add_cycle_cnt()
        self.compute_cycle_energy()


    def stall_out(self):
        return None

    def compute_cycle_energy(self):
        pass


    def update(self):
        self.pc = self.next_pc



