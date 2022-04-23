from Core.Instruction.inst import instruction
from Core.Stage.base import StageBase


VEU_INST = []
SEU_INST = []
MEU_INST = []
DTU_INST = []



# 这里不模拟bypass到seu的效果了
class Issue(StageBase):
    def __init__(self):
        super(Issue, self).__init__()
        # self.send_data = {'eu':'none','inst':instruction()}

    def set_pos_reg(self):
        self.stage_reg.stage_data = self.pre_stage_list[0].send_data
        print(self.stage_reg.stage_data.op)

    @property
    def send_data(self):
        return {'eu':self.eu_dispatch(),'inst':self.stage_reg.stage_data}

    def pos_tick(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

    def stall_info(self):
        pass

    def compute_cycle_energy(self):
        pass

    def eu_dispatch(self):
        stage_data = self.stage_reg.stage_data
        if stage_data.op[0] == 'v':
            current_eu = 'veu'
        elif stage_data.op[0] == 's' and stage_data.op not in ['send','st','sti']:
            current_eu = 'seu'
        elif stage_data.op in {'send','recv','ld','st','sti','ldi'}:
            current_eu = 'dtu'
        elif stage_data.op in {'bind','unbind','gemv','gvr'}:
            current_eu = 'meu'
        else:
            current_eu = 'none'
            print( "no eu candidate")

        return current_eu


    def bypass_ticktock(self):
        return {'eu':self.eu_dispatch(),'inst':self.stage_data}