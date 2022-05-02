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

    # 重载为了实现堆的构建
    def __cmp__(self, other):
        if self.pending_cycles < other.pending_cycles:
            return -1
        elif self.pending_cycles > other.pending_cycles:
            return 1
        return 0

    def __lt__(self, other):
        return self.pending_cycles < other.pending_cycles


    def __gt__(self, other):
        return self.pending_cycles > other.pending_cycles


    def __eq__(self, other):
        return self.pending_cycles == other.pending_cycles



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
    def __init__(self,mesh_layout):
        self.mesh_layout = mesh_layout
        self.mesh_row,self.mesh_column = self.mesh_layout


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


    def add_gateway(self,gateway):
        gateway_id = gateway.gateway_id
        self.gateway_dict[gateway_id] = gateway
        self.pending_event_dict[gateway_id] = PendingQueue()

