from typing import List

from Core.PipeLine.base import PipeLineBase
from Core.PipeLine.comm import BlockedGateway
from Core.Stage.base import StageBase
from Config.config import SimConfig


from Core.Stage.fetch import Fetch
from Core.Stage.decoder import Decoder
from Core.Stage.issue import Issue
from Core.Stage.matrix import Matrix
from Core.Stage.stall import StallEngine
from Core.Stage.vector import Vector
from Core.Stage.transfer import Transfer
from Core.Stage.scalar import Scalar
from Core.Stage.memQueue import MemQueue


from Core.Stage.Storage.regFile import RegFile
from Core.Stage.Storage.mem import ScratchPad



class TinyCore(PipeLineBase):
    def __init__(self,core_id):
        super(TinyCore, self).__init__()
        self.core_id = core_id

        self.reg_file = RegFile()
        self.scratchpad = ScratchPad()
        self.config = SimConfig()


        self.if_stage = Fetch()
        self.id_stage = Decoder()
        self.ri_stage = Issue()

        self.mem_queue = MemQueue(self.reg_file)
        self.meu_stage = Matrix(self,self.scratchpad)
        self.veu_stage = Vector(self.scratchpad)
        self.dtu_stage = Transfer(self.scratchpad)

        self.seu_stage = Scalar(self.reg_file)


        self.stall_engine = StallEngine()
        for k,stage in self._stages.items():
            stage.set_stall_engine(self.stall_engine)


    def structure(self,head_stage) -> List[StageBase]:
        # 构建流水线架构
        self.if_stage.connect_to(head_stage)
        self.id_stage.connect_to(self.if_stage)
        self.ri_stage.connect_to(self.id_stage)

        self.seu_stage.connect_to(self.ri_stage)
        self.mem_queue.connect_to(self.ri_stage)
        #
        self.meu_stage.connect_to(self.mem_queue)
        self.veu_stage.connect_to(self.mem_queue)
        self.dtu_stage.connect_to(self.mem_queue)


        # 旁路部分
        # self.mem_queue.bypass_connect_to(self.veu_stage,self.dtu_stage)
        # self.dtu_stage.bypass_connect_to(self.mem_queue)
        # # self.meu_stage.bypass_connect_to(self.mem_queue) # 不是这条旁路
        # self.veu_stage.bypass_connect_to(self.mem_queue)
        self.mem_queue.bypass_connect_to(self.veu_stage) # 用于删除操作
        self.mem_queue.bypass_connect_to(self.dtu_stage)
        # self.mem_queue.bypass_connect_to(self.meu_stage)

        # return [self.meu_stage,self.veu_stage,self.dtu_stage]

        return [self.veu_stage]

    def load_dict(self,file_name):
        self.if_stage.load_dict(file_name)

    def forward_one_cycle(self):
        super(TinyCore, self).forward_one_cycle()
        self.stall_engine.update()
        # self.print_info()

    def set_gateway(self,gateway):
        self.dtu_stage.set_gateway(gateway)

    def check_halt(self):
        state = True
        for k,stage in self._stages.items():
            # if isinstance(stage,Fetch):
            #     print('pc:{}'.format(stage.inner_reg.pc))
            if stage.stage_reg.stage_data.op != 'none':
                state = False
                break
        return state


    def compute_total_energy(self):

        for k,stage in self._stages.items():
            self.total_energy += stage.compute_total_energy()

        self.total_energy += self.scratchpad.compute_total_energy(self.total_cycles)
        self.total_energy += self.reg_file.compute_total_energy(self.total_cycles)

        return self.total_energy