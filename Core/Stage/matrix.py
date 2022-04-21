from collections import OrderedDict

from Core.Stage.Storage.regFile import RegFile
from Core.Stage.base import StageBase
from Core.Utils.reg import Register
from Core.Utils.stall import StallEvent


class MatrixGroup(StageBase):
    def __init__(self,packet_id,meu_num):
        super(MatrixGroup, self).__init__()
        self.packet_id = packet_id
        self.meu_num = meu_num

        self.info = None
        self.current_eu = None

        self.inner_reg = Register()
        self.inner_reg.busy_cycle = 0
        self.inner_reg.state = 'idle'

        self.stall_reg = Register()
        self.stall_reg.stalled = False
        self.stall_event = None


    def ticktock(self):
        self.add_cycle_cnt()
        self.compute_cycle_energy()

        if self.inner_reg.state == 'idle':
            if self.current_eu == 'meu':
                cycles = self.set_busy_cycle()
                self.inner_reg.busy_cycle = cycles

                if cycles > 0:
                    self.inner_reg.state = 'busy'

        if self.inner_reg.state == 'busy':
            if self.inner_reg.busy_cycle -1 == 0:
                self.inner_reg.state = 'idle'
            self.inner_reg.busy_cycle = self.inner_reg.busy_cycle - 1


        self.inner_reg.update()


    def update(self):
        if self.check_not_stalled():
            if self.inner_reg.state == 'idle':
                self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']
                self.info = self.recv_data

    def stall_out(self):

        self.stall_event = None
        if self.stall_reg.stalled:
            if self.inner_reg.state == 'idle':
                self.stall_event = StallEvent('MatrixExecuteUnit',False)
                self.stall_reg.stalled = False
        else:
            if self.inner_reg.state == 'busy':
                bypass_info = self.bypass_pre_stage_list[0].bypass_ticktock()
                eu, inst = bypass_info['eu'], bypass_info['inst']
                if eu == 'meu':
                    self.stall_reg.stalled = True
                    self.stall_event = StallEvent('MatrixExecuteUnit', True)

        self.stall_reg.update()
        return self.stall_event

    def compute_cycle_energy(self):
        pass

    def set_busy_cycle(self):
        return  5

    def bypass_ticktock(self):
        if self.stage_data.op == 'gvr':
            if self.inner_reg.state == 'busy':
                if self.inner_reg.busy_cycle -1 == 0:
                    return (self.info.rd_value,self.info.rd_value+self.info.length-1)
        return None





class Matrix(StageBase):
    def __init__(self):
        super(Matrix, self).__init__()
        self.info = None
        self.current_eu = None

        self.meu_dict = OrderedDict()


    def ticktock(self):
        # 这里创建meu，解析一下bind指令
        if self.stage_data.op == 'bind':
            packet_id = self.info.rd_value
            num = self.info.imm
            tmp_meu = MatrixGroup(packet_id, num)
            self.meu_dict[packet_id] = tmp_meu
            for stage in self.pre_stage_list:
                tmp_meu.connect_to(stage)
                tmp_meu.bypass_connect_to(stage)
                stage.bypass_connect_to(tmp_meu)

            for stage in self.post_stage_list:
                stage.connect_to(tmp_meu)

    def update(self):
        self.info = self.recv_data
        self.current_eu,self.stage_data = self.recv_data['eu'],self.recv_data['inst']



    def stall_out(self):
        # 理论上来所，应该只有一个部件能够发出stall,一个发出后另一个就不能发出了
        # for k,v in self.meu_dict.items():
        #     stall_event = v.stall_out()
        #     if stall_event:
        #         return stall_event
        return None

    def compute_cycle_energy(self):
        pass

    def compute_total_energy(self):
        return 0

    def bypass_ticktock(self):
        pass