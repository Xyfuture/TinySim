

from Core.Stage.base import StageBase


VEU_INST = []
SEU_INST = []
MEU_INST = []
DTU_INST = []



# 这里不模拟bypass到seu的效果了
class Issue(StageBase):
    def __init__(self):
        super(Issue, self).__init__()


    def ticktock(self):
        self.send_data = {'eu':self.eu_dispatch(),'inst':self.stage_data}

        self.add_cycle_cnt()
        self.compute_cycle_energy()

    def stall_out(self):
        return None

    def update(self):
        if self.check_not_stalled():
            self.stage_data = self.recv_data

    def compute_cycle_energy(self):
        pass


    def eu_dispatch(self):
        pass


    def bypass_ticktock(self):
        return {'eu':self.eu_dispatch(),'inst':self.stage_data}