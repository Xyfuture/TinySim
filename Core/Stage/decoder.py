

from Core.Stage.base import StageBase


class Decoder(StageBase):
    def __init__(self):
        super(Decoder, self).__init__()


    def set_pos_reg(self):
        self.stage_reg.stage_data = self.pre_stage_list[0].send_data


    def pos_tick(self):
        self.compute_cycle_energy()
        self.add_cycle_cnt()

    @property
    def send_data(self):
        return self.stage_reg.stage_data

    def stall_info(self):
        pass


    def compute_cycle_energy(self):
        pass
