from abc import ABCMeta,abstractmethod
from collections import OrderedDict
from typing import List
import queue


from Core.PipeLine.misc import MetaStage
from Core.Stage.base import StageBase


class PipeLineBase(metaclass=ABCMeta):
    def __init__(self):
        self.head_stage = MetaStage()
        self.tail_stage = MetaStage()


    @abstractmethod
    def structure(self,head_stage)-> List[StageBase]:
        pass
    # 记得return最终输出的所有stage

    #完成构建整个流水线图结构
    def build(self):
        ret = self.structure(self.head_stage)
        self.tail_stage.connect_to(*ret)


    def ticktock_forward(self):
        Q = queue.Queue()
        Q.put(self.head_stage)
        visited =  [self.head_stage] # 因为stage类不一定支持hash功能，所以牺牲一些性能，使用list
        while not Q.empty():
            cur_stage = Q.get()
            cur_stage.ticktock()

            for stage in cur_stage.post_stage_list:
                if stage not in visited:
                    visited.append(stage)
                    Q.put(stage)


    def stall_event_backward(self, stall_stage:StageBase, event):
        Q = queue.Queue()
        visited = []
        # stage本身不需要stall
        for stage in stall_stage.pre_stage_list:
            Q.put(stage)
            visited.append(stage)

        # 采取BFS的方式向前传递event信息
        while not Q.empty():
            cur_stage = Q.get()
            cur_stage.stall_in(event)

            for stage in cur_stage.pre_stage_list:
                if stage not in visited:
                    visited.append(stage)
                    Q.put(stage)

    def stall_forward(self):
        Q = queue.Queue()
        Q.put(self.head_stage)
        visited = [self.head_stage]
        while not Q.empty():
            cur_stage = Q.get()
            ret = cur_stage.stall_out()

            # 如果有需要向外发送的stall信息
            if ret:
                self.stall_event_backward(cur_stage,ret)

            for stage in cur_stage.post_stage_list:
                if stage not in visited:
                    visited.append(stage)
                    Q.put(stage)



    def transfer_forward(self):
        Q = queue.Queue()
        Q.put(self.head_stage)
        visited = [self.head_stage]
        while not Q.empty():
            cur_stage = Q.get()
            tmp_data = cur_stage.send()
            for stage in cur_stage.post_stage_list:
                stage.recv(tmp_data)
                if stage not in visited:
                    visited.append(stage)
                    Q.put(stage)


    def update_forward(self):
        Q = queue.Queue()
        Q.put(self.head_stage)
        visited = [self.head_stage]

        while not Q.empty():
            cur_stage = Q.get()
            cur_stage.update()

            for stage in cur_stage.post_stage_list:
                if stage not in visited:
                    visited.append(stage)
                    Q.put(stage)


    def forward_one_cycle(self):
        self.update_forward()
        self.ticktock_forward()
        self.stall_forward()
        self.transfer_forward()





