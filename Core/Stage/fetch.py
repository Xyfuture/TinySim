

from Core.Stage.base import StageBase
from Core.Instruction.inst import InstBuffer, instruction
from Core.Utils.reg import Register


class Fetch(StageBase):
    def __init__(self):
        super(Fetch, self).__init__()
        self.level = 1

        self.inst_buffer = InstBuffer()
        self.inst_count = 0

        self.inner_reg = Register()
        self.inner_reg.pc = 0


    def set_pos_reg(self):
        if self.stall_engine.check_not_stall(self.level):
            self.inner_reg.pc = self.inner_reg.pc+1

    def pos_tick(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        # if self.inner_reg.pc < self.inst_count:
        #     self.send_data = self.inst_buffer[self.inner_reg.pc]
        # else:
        #     self.send_data = instruction()
        # self.inner_reg.pc = self.inner_reg.pc + 1
    @property
    def send_data(self):
        if self.inner_reg.pc < self.inst_count:
            return self.inst_buffer[self.inner_reg.pc]
        else:
            return instruction()

    def stall_info(self):
        return None

    def compute_cycle_energy(self):
        pass


    def load_dict(self,file_name):
        self.inst_buffer.load_dict(file_name)
        self.inst_count = self.inst_buffer.get_inst_count()

    def dump_info(self):
        return ('Fetch:\n'
              'inst:{}\n'
              'stall:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level)))