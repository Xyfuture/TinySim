from collections import OrderedDict
from abc import ABCMeta,abstractmethod

from Core.Instruction.inst import instruction


# 在这个里面不仅记录了每个stage传输的信息还记录了各个stage之间的连接关系
# 遍历应该遵循bfs的顺序，不能直接在这个类里面实现
from Core.Utils.stall import StallEvent


class StageBase(metaclass=ABCMeta):
    def __init__(self):
        self.stage_data = instruction()
        self.recv_data = instruction()
        self.send_data = instruction()

        self.total_energy = 0
        self.total_cycles = 0
        self.stall_cycles = 0

        self.pre_stage_list = [] # 构建连接关系
        self.post_stage_list = []

        self.bypass_pre_stage_list = []

        self.stall_info_dict = OrderedDict()

        self.gateway = None

    def recv(self,pre_stage_data):
        self.recv_data = pre_stage_data


    def send(self):
        return  self.send_data

    # 处理当前的stage_data ,同时计算功耗等信息
    @abstractmethod
    def ticktock(self):
        pass

    # 根据收到的信息更新stage_data
    @abstractmethod
    def update(self):
        pass

    # 当前stage对其他stage是否产生stall,return None 表示没有stall发生
    @abstractmethod
    def stall_out(self):
        pass

    # 一个周期的
    @abstractmethod
    def compute_cycle_energy(self):
        pass

    # 其他stage产生的stall信息传到当前stage
    def stall_in(self,stall_event:StallEvent):
        if stall_event.state:
            self.stall_info_dict[stall_event.stage_name] = True
        else:
            del self.stall_info_dict[stall_event.stage_name]


    # 构建连接关系
    def connect_to(self,*pre_stages):
        for stage in pre_stages:
            self.pre_stage_list.append(stage)
            stage.add_post_stage(self)

    def add_pre_stage(self,s):
        self.pre_stage_list.append(s)

    def add_post_stage(self,s):
        self.post_stage_list.append(s)


    def compute_total_energy(self):
        return self.total_energy


    def add_cycle_cnt(self):
        self.total_cycles += 1
        if self.check_stalled():
            self.stall_cycles += 1

    def check_stalled(self):
        return len(self.stall_info_dict) == 0

    def check_not_stalled(self):
        return not self.check_stalled()

    # 与Core外进行数据传输
    def set_gateway(self,g):
        self.gateway = g

    def bypass_connect_to(self,*pre_stages):
        for stage in pre_stages:
            self.bypass_pre_stage_list.append(stage)
            # 这个不维持完整的连接了，只保证后面的可以连接到前面的。

    # 该调用只返回一个结果，并不对self进行任何更改，也不计算能耗等信息
    def bypass_ticktock(self):
        return None