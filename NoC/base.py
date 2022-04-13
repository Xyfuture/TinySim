import heapq
from collections import OrderedDict
from abc import ABCMeta,abstractmethod
from typing import List

from NoC.packet import  DataPacket


class PendingEvent:
    def __init__(self,pending_cycles,packet,call_back=None,describe=None):
        self.pending_cycles = pending_cycles
        self.packet:DataPacket = packet
        self.call_back = call_back
        self.describe = describe

    def __cmp__(self, other):
        pass


class PendingQueue:
    def __init__(self):
        self.event_list:List[PendingEvent] = []

    def push(self,item:PendingEvent):
        heapq.heappush(self.event_list,item)

    def pop(self):
        return heapq.heappop(self.event_list)

    # 进行一个周期并进行响应的处理
    def update(self):
        for event in self.event_list:
            event.pending_cycles -= 1
            if event.pending_cycles == 0:
                if callable(event.call_back):
                    event.call_back(event.packet)
                self.event_list.remove(event)



class NoCBase(metaclass=ABCMeta):
    def __init__(self):

        self.gateway_dict = {}
        self.pending_event_dict = {}

        self.total_energy = 0


    @abstractmethod
    def compute_transfer_latency(self,packet:DataPacket):
        pass

    @abstractmethod
    def compute_transfer_energy(self,packet:DataPacket):
        pass

    # GateWay调用该模块想其他模块发送数据
    @abstractmethod
    def send(self,packet:DataPacket):
        pass


    def ticktock(self):
        for i,event_list in self.pending_event_dict.items():
            event_list.update()





