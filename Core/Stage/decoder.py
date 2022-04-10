from Core.Stage.base import StageBase


class Decoder(StageBase):
    def __init__(self):
        super(Decoder, self).__init__()


    def recv(self,pre_stage_data):
        self.recv_data = pre_stage_data

    def send(self):
        return self.send_data

    def ticktock(self):
        self.send_data = self.stage_data

        self.compute_cycle_enery()
        self.add_cycle_cnt()

    def stall_out(self):
        return None

    def update(self):
        if self.check_not_stalled():
            self.stage_data = self.recv_data

    def compute_cycle_enery(self):
        pass
