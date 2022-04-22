from typing import List

from Core.PipeLine.base import PipeLineBase
from Core.PipeLine.comm import BlockedGateway
from Core.Stage.base import StageBase
from Config.config import SimConfig


from Core.Stage.fetch import Fetch
from Core.Stage.decoder import Decoder
from Core.Stage.issue import Issue
from Core.Stage.matrix import Matrix
from Core.Stage.vector import Vector
from Core.Stage.transfer import Transfer
from Core.Stage.scalar import Scalar
from Core.Stage.memQueue import MemQueue


from Core.Stage.Storage.regFile import RegFile


class TinyCore(PipeLineBase):
    def __init__(self,core_id):
        super(TinyCore, self).__init__()
        self.core_id = core_id

        self.reg_file = RegFile()
        self.config = SimConfig()


        self.if_stage = Fetch()
        self.id_stage = Decoder()
        self.ri_stage = Issue()

        self.mem_queue = MemQueue(self.reg_file)
        self.meu_stage = Matrix()
        self.veu_stage = Vector()
        self.dtu_stage = Transfer()

        self.seu_stage = Scalar(self.reg_file)

    def structure(self,head_stage) -> List[StageBase]:
        # 构建流水线架构
        self.if_stage.connect_to(head_stage)
        self.id_stage.connect_to(self.if_stage)
        self.ri_stage.connect_to(self.id_stage)

        self.seu_stage.connect_to(self.ri_stage)
        self.meu_stage.connect_to(self.ri_stage)
        self.veu_stage.connect_to(self.ri_stage)
        self.dtu_stage.connect_to(self.ri_stage)


        # 旁路部分
        self.ri_stage.bypass_connect_to(self.meu_stage,self.veu_stage,self.dtu_stage)
        self.dtu_stage.bypass_connect_to(self.ri_stage)
        self.meu_stage.bypass_connect_to(self.ri_stage)
        self.veu_stage.bypass_connect_to(self.ri_stage)

        return [self.meu_stage,self.veu_stage,self.dtu_stage]


    def load_dict(self,file_name):
        self.if_stage.load_dict(file_name)