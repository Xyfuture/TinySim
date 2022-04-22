

from Core.Stage.base import StageBase
from Core.Instruction.inst import InstBuffer, instruction
from Core.Utils.reg import Register


class Fetch(StageBase):
    def __init__(self):
        super(Fetch, self).__init__()

        # self.pc = 0
        # self.next_pc = 0
        self.inst_buffer = InstBuffer()
        self.inst_count = 0

        self.inner_reg = Register()
        self.inner_reg.pc = 0

    def ticktock(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.inner_reg.pc < self.inst_count:
            self.send_data = self.inst_buffer[self.inner_reg.pc]
        else:
            self.send_data = instruction()
        self.inner_reg.pc = self.inner_reg.pc + 1


    def stall_out(self):
        return None

    def compute_cycle_energy(self):
        pass


    def update(self):
        # 没有被stall的时候正常进行更新
        if self.check_not_stalled():
            self.inner_reg.update()


    def load_dict(self,file_name):
        self.inst_buffer.load_dict(file_name)
        self.inst_count = self.inst_buffer.get_inst_count()
