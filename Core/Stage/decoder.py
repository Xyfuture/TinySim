

from Core.Stage.base import StageBase


class Decoder(StageBase):
    def __init__(self):
        super(Decoder, self).__init__()
        self.level = 2

        self.dynamic_per_energy = 0.31074
        self.leakage_per_energy = 0.0014557



    def set_pos_reg(self):
        if self.stall_engine.check_not_stall(self.level):
            self.stage_reg.stage_data = self.pre_stage_list[0].send_data


    def pos_tick(self):
        self.compute_dynamic_energy()
        self.add_cycle_cnt()

    @property
    def send_data(self):
        return self.stage_reg.stage_data

    def stall_info(self):
        return None


    def compute_dynamic_energy(self):
        if self.stall_engine.check_not_stall(self.level):
            self.dynamic_energy += self.dynamic_per_energy

    def compute_leakage_energy(self):
        self.leakage_energy = self.leakage_per_energy * self.total_energy

    def dump_info(self):
        return  ('Decoder:\n'
              'inst:{}\n'
              'stall:{}\n'.format(self.stage_reg.stage_data.dump_asm(),self.stall_engine.check_stall(self.level)))