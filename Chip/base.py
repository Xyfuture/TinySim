from abc import ABCMeta,abstractmethod

from NoC.block import BlockedNoc


class ChipTop:
    def __init__(self):
        self.core_dict = {}
        self.gateway_dict = {}
        self.noc_bus = BlockedNoc()

    def run(self):
        # 运行整个芯片
        pass