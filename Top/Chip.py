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
        self.cycles = 0
        self.core_halt_state = {}

    def run_cycle(self):
        # 运行整个芯片
        for k,core in self.core_dict.items():
            if not self.core_halt_state[k]:
                core.forward_one_cycle()
        self.noc_bus.ticktock()

    def run_all(self):

        for i in self.core_dict:
            self.core_halt_state[i] = False #没有halt

        while True:
            self.run_cycle()
            # print(self.cycles)
            # if self.cycles ==1734:
            #     print('here')
            if self.cycles%1000 == 0:
                # print("cycles: {}".format(self.cycles))
                for core_id in list(self.core_halt_state.keys()):
                    if not self.core_halt_state[core_id]:
                        self.core_halt_state[core_id] = self.core_dict[core_id].check_halt()
                        # print('core_id:{} pc:{}'.format(core_id,self.core_dict[core_id].if_stage.inner_reg.pc))
                chip_halt_state = True
                for k,v in self.core_halt_state.items():
                    if not v:
                        chip_halt_state = False
                        break
                if chip_halt_state:
                    break
            self.cycles += 1
        return self.cycles
    def build(self):
        # 构建 core 和 gateway
        # core_id = 0
        for i in range(self.mesh_layout[0]):
            for j in range(self.mesh_layout[1]):
                core_id = i*self.mesh_layout[1] + j

                tmp_core = TinyCore(core_id)
                tmp_core.build()

                tmp_gateway = BlockedGateway(self.noc_bus,core_id)

                self.noc_bus.add_gateway(tmp_gateway)
                self.gateway_dict[core_id] = tmp_gateway
                self.core_dict[core_id] = tmp_core

                tmp_core.set_gateway(tmp_gateway)

    def load_dict(self,dir_name):
        for i in range(self.mesh_layout[0]):
            for j in range(self.mesh_layout[1]):
                core_id = i* self.mesh_layout[1] + j
                tmp_file_name = dir_name+"{}.pkl".format(core_id)
                tmp_core = self.core_dict[core_id]
                tmp_core.load_dict(tmp_file_name)
