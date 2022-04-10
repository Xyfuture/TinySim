

# from Core.Stage.Storage.regFile import
from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase


class Scalar(StageBase):
    def __init__(self,reg_file:RegFile):
        super(Scalar, self).__init__()

        self.reg_file = reg_file
        self.current_eu = None



    def ticktock(self):
        if self.current_eu == 'seu':
            self.scalar_excute()

        self.add_cycle_cnt()
        self.compute_cycle_energy()



    def update(self):
        self.current_eu = self.recv_data['eu']
        self.stage_data = self.recv_data['inst']

    def stall_out(self):
        return None

    def compute_cycle_energy(self):
        pass

    def scalar_excute(self):
        pass