from abc import ABCMeta,abstractmethod

from Config.config import SimConfig
from Core.PipeLine.comm import BlockedGateway
from NoC.block import BlockedNoc
from Top.TinyCore import TinyCore


class ChipTop:
    def __init__(self):
        self.config = SimConfig()
        self.mesh_layout = self.config.mesh_layout

        self.core_dict = {}
        self.gateway_dict = {}
        self.noc_bus = BlockedNoc(self.mesh_layout)

    def run(self):
        # 运行整个芯片
        for k,core in self.core_dict.items():
            core.forward_one_cycle()
        self.noc_bus.ticktock()


    def build(self):
        # 构建 core 和 gateway
        # core_id = 0
        for i in range(self.mesh_layout[0]):
            for j in range(self.mesh_layout[1]):
                core_id = i*self.mesh_layout[1] + j

                tmp_core = TinyCore(core_id)
                tmp_gateway = BlockedGateway(self.noc_bus,core_id)

                self.noc_bus.add_gateway(tmp_gateway)
                self.gateway_dict[core_id] = tmp_gateway
                self.core_dict[core_id] = tmp_core


