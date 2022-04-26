from abc import ABCMeta,abstractmethod
from collections import OrderedDict
from typing import List
import queue


from Core.PipeLine.misc import MetaStage
from Core.Stage.base import StageBase


class PipeLineBase(metaclass=ABCMeta):
    def __init__(self):
        self._stages = OrderedDict()

        self.head_stage = MetaStage()
        self.tail_stage = MetaStage()

        # self.build()

    def __setattr__(self, key, value):
        if isinstance(value,StageBase):
            self._stages[key] = value

        super(PipeLineBase, self).__setattr__(key,value)



    @abstractmethod
    def structure(self,head_stage)-> List[StageBase]:
        pass
    # 记得return最终输出的所有stage

    #完成构建整个流水线图结构
    def build(self):
        ret = self.structure(self.head_stage)
        self.tail_stage.connect_to(*ret)

    def set_pos_reg(self):
        for k,stage in self._stages.items():
            stage.set_pos_reg()

    def posedge(self):
        for k,stage in self._stages.items():
            stage.posedge()

    def pos_tick(self):
        # 支持向dict里面动态添加
        for k in list(self._stages.keys()):
            stage = self._stages[k]
        # for k,stage in self._stages.items():
            stage.pos_tick()

    def set_neg_reg(self):
        for k,stage in self._stages.items():
            stage.set_neg_reg()

    def negedge(self):
        for k,stage in self._stages.items():
            stage.negedge()

    def neg_tick(self):
        for k,stage in self._stages.items():
            stage.neg_tick()

    def forward_one_cycle(self):
        self.set_pos_reg()
        self.posedge()
        self.pos_tick()

        self.set_neg_reg()
        self.negedge()
        self.neg_tick()

    def print_info(self):
        for k,stage in self._stages.items():
            stage.print_info()


