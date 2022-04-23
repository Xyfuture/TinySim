from Core.Stage.base import StageBase


# 供PipeLineBase的head和tail使用
class MetaStage(StageBase):
    def __init__(self):
        super(MetaStage, self).__init__()

    def set_pos_reg(self):
        pass

    def stall_info(self):
        pass

    def send_data(self):
        return 0

    def compute_cycle_energy(self):
        return 0

