from Core.Stage.base import StageBase


# 供PipeLineBase的head和tail使用
class MetaStage(StageBase):
    def __init__(self):
        super(MetaStage, self).__init__()

    def recv(self,pre_stage_data=None):
        pass

    def send(self):
        return None

    def ticktock(self):
        pass

    def stall_out(self):
        pass

    def compute_total_energy(self):
        return 0

    def update(self):
        pass