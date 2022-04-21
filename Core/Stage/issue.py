

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
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        self.send_data = {'eu':self.eu_dispatch(),'inst':self.stage_data}


    def stall_out(self):
        return None

    def update(self):
        if self.check_not_stalled():
            self.stage_data = self.recv_data

    def compute_cycle_energy(self):
        pass

    def eu_dispatch(self):
        if self.stage_data.op[0] == 'v':
            current_eu = 'veu'
        elif self.stage_data.op[0] == 's' and self.stage_data.op not in ['send','st','sti']:
            current_eu = 'seu'
        elif self.stage_data.op in {'send','recv','ld','st','sti','ldi'}:
            current_eu = 'dtu'
        elif self.stage_data.op in {'bind','unbind','gemv','gvr'}:
            current_eu = 'meu'
        else:
            raise "no eu candidate"

        return current_eu


    def bypass_ticktock(self):
        return {'eu':self.eu_dispatch(),'inst':self.stage_data}