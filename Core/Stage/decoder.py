

from Core.Stage.base import StageBase


class Decoder(StageBase):
    def __init__(self):
        super(Decoder, self).__init__()

    def ticktock(self):
        self.compute_cycle_energy()
        self.add_cycle_cnt()

        self.send_data = self.stage_data



    def stall_out(self):
        return None

    def update(self):
        if self.check_not_stalled():
            self.stage_data = self.recv_data

    def compute_cycle_energy(self):
        pass
